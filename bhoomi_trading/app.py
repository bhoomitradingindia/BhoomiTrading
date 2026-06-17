import os
import json
from datetime import datetime
from urllib.parse import quote_plus

from flask import Flask, render_template, request, redirect, jsonify, session
import gspread
from google.oauth2.service_account import Credentials
from pymongo import MongoClient
from bson import ObjectId


app = Flask(__name__)

# =========================
# ADMIN LOGIN CONFIG
# =========================

app.secret_key = os.getenv("FLASK_SECRET_KEY", "bhoomi_admin_secret_2026")

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminxyz")

# =========================
# BASE PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CREDS_FILE = os.path.join(BASE_DIR, "enq_logs.json")
GOOGLE_SHEET_NAME = "Bhoomi Trading Enquiries"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =========================
# MONGODB ATLAS CONNECTION
# =========================

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    _username = quote_plus("sandeshpimpale2606_db_user")
    _password = quote_plus("8928223266@Sp")
    MONGO_URI = (
        f"mongodb+srv://{_username}:{_password}"
        f"@bhoomitrading.lrdbstj.mongodb.net/bhoomi_trading"
        f"?retryWrites=true&w=majority&appName=BhoomiTrading"
    )
    print("WARNING: MONGO_URI env variable not set. Using hardcoded credentials as fallback.")

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")
    print("✅ MongoDB Atlas connected successfully")
except Exception as e:
    print(f"❌ FATAL: Could not connect to MongoDB Atlas: {e}")
    raise SystemExit("MongoDB connection failed. Set a valid MONGO_URI environment variable.")

# =========================
# ALL COLLECTIONS
# =========================

db = mongo_client["bhoomi_trading"]

enquiries_collection  = db["enquiries"]    # website contact form + API enquiries
materials_collection  = db["materials"]    # existing catalogue items used by current website
users_collection      = db["users"]        # registered / tracked users (future-ready)
admin_logs_collection = db["admin_logs"]   # every admin action is logged here

# Extra business collections for proper MongoDB structure
customers_collection  = db["customers"]    # auto-created from enquiry/contact form data
settings_collection   = db["settings"]     # company/contact configuration
categories_collection = db["categories"]   # material/product categories
products_collection   = db["products"]     # product list if you want separate products collection later

# =========================
# COMPANY DATA
# =========================

company = {
    "established": "2026",
    "tagline": "Quality Materials for Bags, Purses & Creative Designs",
    "description": (
        "Bhoomi Trading supplies quality bag-making materials including "
        "Rexine, Leather, Canvas, Nylon Fabric and Polyester Fabric."
    ),
    "phone": "+91 9876543210",
    "email": "bhoomitradingindia@gmail.com",
    "whatsapp": "919833037930"
}

services_data = [
    {
        "icon": "🧵",
        "title": "Material Supply",
        "description": "We provide quality bag-making materials for retail and business requirements.",
        "highlights": ["Rexine", "Leather", "Canvas", "Lining Fabric"]
    },
    {
        "icon": "📦",
        "title": "Wholesale Orders",
        "description": "Bulk material supply for bag makers, workshops and manufacturers.",
        "highlights": ["Bulk quantity", "Material variety", "Reliable supply"]
    },
    {
        "icon": "💬",
        "title": "Customer Enquiry Support",
        "description": "Customers can directly enquire about materials through WhatsApp, phone or email.",
        "highlights": ["WhatsApp enquiry", "Quick response", "Direct communication"]
    }
]

# =========================
# HELPER FUNCTIONS
# =========================

def create_material_id(name):
    """Create a slug-style ID from a material name."""
    return name.lower().strip().replace(" ", "-")


def serialize_doc(doc):
    """Convert a MongoDB document to a JSON-safe dict."""
    if doc is None:
        return None
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if "created_at" in doc and not isinstance(doc["created_at"], str):
        doc["created_at"] = str(doc["created_at"])
    if "updated_at" in doc and not isinstance(doc["updated_at"], str):
        doc["updated_at"] = str(doc["updated_at"])
    return doc


def log_admin_action(action, details=None):
    """Save every admin action to the admin_logs collection in Atlas."""
    try:
        admin_logs_collection.insert_one({
            "action": action,
            "details": details or {},
            "performed_by": session.get("admin_username", "admin"),
            "timestamp": datetime.now()
        })
    except Exception as e:
        print(f"Admin log error: {e}")


def save_or_update_customer(data):
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()

    if not phone and not email:
        return None

    customer_filter = {"$or": []}

    if phone:
        customer_filter["$or"].append({"phone": phone})

    if email:
        customer_filter["$or"].append({"email": email})

    customer_data = {
        "name": data.get("name", ""),
        "phone": phone,
        "email": email,
        "source": data.get("source", "")
    }

    return customers_collection.update_one(
        customer_filter,
        {
            "$set": customer_data,
            "$unset": {
                "last_material_enquired": "",
                "last_message": "",
                "last_enquiry_at": "",
                
                "created_at": "",
                "updated_at": ""
            }
        },
        upsert=True
    )


def save_enquiry_to_google_sheet(data):
    """Backup enquiry to Google Sheets (non-blocking; errors are caught by caller)."""
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")

    if credentials_json:
        creds_info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)

    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1

    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        data.get("name", ""),
        data.get("phone", ""),
        data.get("email", ""),
        data.get("material", ""),
        data.get("message", "")
    ])


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def home():
    materials = list(materials_collection.find())
    featured = [serialize_doc(m) for m in materials[:4]]
    return render_template("home.html", company=company, featured=featured)


@app.route("/catalogue")
def catalogue():
    # All materials stored in Atlas — loaded fresh on every page visit
    materials = [serialize_doc(m) for m in materials_collection.find()]
    return render_template("catalogue.html", company=company, materials=materials)


@app.route("/services")
def services():
    return render_template("services.html", company=company, services=services_data)


@app.route("/contact")
def contact():
    return render_template("contact.html", company=company)


# =========================
# ADMIN ROUTES
# =========================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            session["admin_username"] = username

            # Log the login event to Atlas
            admin_logs_collection.insert_one({
                "action": "admin_login",
                "performed_by": username,
                "timestamp": datetime.now()
            })

            return redirect("/admin/dashboard")

        # Log failed attempt to Atlas
        admin_logs_collection.insert_one({
            "action": "admin_login_failed",
            "attempted_username": username,
            "timestamp": datetime.now()
        })

        return render_template(
            "admin_login.html",
            company=company,
            error="Invalid username or password"
        )

    return render_template("admin_login.html", company=company)


@app.route("/admin/logout")
def admin_logout():
    log_admin_action("admin_logout")
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect("/admin/login")


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    materials  = [serialize_doc(m) for m in materials_collection.find()]
    enquiries  = [serialize_doc(e) for e in enquiries_collection.find()]
    users      = [serialize_doc(u) for u in users_collection.find()]
    customers  = [serialize_doc(c) for c in customers_collection.find()]
    admin_logs = [serialize_doc(l) for l in admin_logs_collection.find().sort("timestamp", -1).limit(20)]

    total_materials  = len(materials)
    total_enquiries  = len(enquiries)
    total_users      = len(users)
    total_customers  = len(customers)

    material_count = {}
    for enq in enquiries:
        mat = enq.get("material", "Unknown")
        material_count[mat] = material_count.get(mat, 0) + 1

    most_requested = "No enquiries yet"
    if material_count:
        most_requested = max(material_count, key=material_count.get)

    return render_template(
        "admin_dashboard.html",
        company=company,
        materials=materials,
        enquiries=enquiries,
        users=users,
        customers=customers,
        admin_logs=admin_logs,
        total_materials=total_materials,
        total_enquiries=total_enquiries,
        total_users=total_users,
        total_customers=total_customers,
        most_requested=most_requested
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":
        subtypes_raw = request.form.get("subtypes", "")
        subtypes = [item.strip() for item in subtypes_raw.split(",") if item.strip()]
        name = request.form.get("name", "")

        new_material = {
            "id": create_material_id(name),
            "name": name,
            "category": request.form.get("category", ""),
            "description": request.form.get("description", ""),
            "image": request.form.get("image", ""),
            "subtypes": subtypes,
            "created_at": datetime.now()
        }

        result = materials_collection.insert_one(new_material)
        log_admin_action("material_added", {"name": name, "id": str(result.inserted_id)})

        return redirect("/admin")

    materials = [serialize_doc(m) for m in materials_collection.find()]
    return render_template("admin.html", company=company, materials=materials)


# =========================
# WEBSITE ENQUIRY FORM ROUTE
# =========================

@app.route("/enquiry", methods=["POST"])
def enquiry():
    enquiry_data = {
        "name":     request.form.get("name", ""),
        "phone":    request.form.get("phone", ""),
        "email":    request.form.get("email", ""),
        "material": request.form.get("material", ""),
        "message":  request.form.get("message", ""),
        "source":   "website_form",
        "created_at": datetime.now()
    }

    try:
        # Save to MongoDB Atlas
        enquiries_collection.insert_one(enquiry_data)

        # Also save/update customer automatically from enquiry form
        save_or_update_customer(enquiry_data)

        print("✅ Enquiry and customer saved to MongoDB Atlas:", enquiry_data.get("name"))
    except Exception as e:
        print("❌ MongoDB enquiry error:", e)

    try:
        # Backup to Google Sheets
        save_enquiry_to_google_sheet(enquiry_data)
        print("✅ Enquiry backed up to Google Sheets")
    except Exception as e:
        print("⚠️  Google Sheets backup failed (enquiry still saved to MongoDB):", e)

    return redirect("/contact")


# =========================
# USER ROUTES (Atlas: users collection)
# =========================

@app.route("/api/users", methods=["GET"])
def get_all_users():
    users = [serialize_doc(u) for u in users_collection.find()]
    return jsonify({"status": "success", "data": users}), 200


@app.route("/api/users", methods=["POST"])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    def build_user_doc(item):
        return {
            "name":       item.get("name", ""),
            "email":      item.get("email", ""),
            "phone":      item.get("phone", ""),
            "address":    item.get("address", ""),
            "created_at": datetime.now()
        }

    # Bulk users from Postman: accepts a JSON list
    if isinstance(data, list):
        inserted_ids = []
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            if not item.get("name") or not item.get("email"):
                skipped.append({"index": index, "reason": "name and email are required"})
                continue

            if users_collection.find_one({"email": item["email"]}):
                skipped.append({"index": index, "reason": "duplicate email", "email": item["email"]})
                continue

            new_user = build_user_doc(item)
            result = users_collection.insert_one(new_user)
            inserted_ids.append(str(result.inserted_id))

        return jsonify({
            "status": "success",
            "message": f"{len(inserted_ids)} users created successfully",
            "ids": inserted_ids,
            "skipped": skipped
        }), 201

    # Single user
    required = ["name", "email"]
    for field in required:
        if not data.get(field):
            return jsonify({"status": "error", "message": f"'{field}' is required"}), 400

    # Prevent duplicate emails
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"status": "error", "message": "User with this email already exists"}), 409

    new_user = build_user_doc(data)
    result = users_collection.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return jsonify({
        "status": "success",
        "message": "User created",
        "data": serialize_doc(new_user)
    }), 201


@app.route("/api/users/<user_id>", methods=["GET"])
def get_single_user(user_id):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    return jsonify({"status": "success", "data": serialize_doc(user)}), 200


@app.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    allowed = ["name", "email", "phone", "address"]
    update_data = {k: v for k, v in data.items() if k in allowed}
    update_data["updated_at"] = datetime.now()

    try:
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404

    updated = serialize_doc(users_collection.find_one({"_id": ObjectId(user_id)}))
    return jsonify({"status": "success", "message": "User updated", "data": updated}), 200


@app.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    try:
        result = users_collection.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "User not found"}), 404

    log_admin_action("user_deleted", {"user_id": user_id})
    return jsonify({"status": "success", "message": "User deleted"}), 200


# =========================
# ENQUIRY API ROUTES (Atlas: enquiries collection)
# =========================

@app.route("/api/enquiry", methods=["POST"])
def create_enquiry():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    def save_api_enquiry(item):
        item["source"] = "api"
        item["created_at"] = datetime.now()
        result = enquiries_collection.insert_one(item)
        save_or_update_customer(item)
        try:
            save_enquiry_to_google_sheet(item)
        except Exception as e:
            print("⚠️ Google Sheets backup failed:", e)
        return str(result.inserted_id)
    
    

    # Bulk enquiries from Postman: accepts a JSON list
    if isinstance(data, list):
        inserted_ids = []
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            inserted_ids.append(save_api_enquiry(item))

        return jsonify({
            "status": "success",
            "message": f"{len(inserted_ids)} enquiries created successfully",
            "ids": inserted_ids,
            "skipped": skipped
        }), 201

    # Single enquiry
    inserted_id = save_api_enquiry(data)

    return jsonify({
        "status": "success",
        "message": "Enquiry created",
        "id": inserted_id
    }), 201


@app.route("/api/enquiries", methods=["GET"])
def get_all_enquiries():
    enquiries = [serialize_doc(e) for e in enquiries_collection.find()]
    return jsonify({"status": "success", "data": enquiries}), 200


@app.route("/api/enquiry/<id>", methods=["GET"])
def get_single_enquiry(id):
    try:
        enq = enquiries_collection.find_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if not enq:
        return jsonify({"status": "error", "message": "Enquiry not found"}), 404

    return jsonify({"status": "success", "data": serialize_doc(enq)}), 200


@app.route("/api/enquiry/<id>", methods=["PUT"])
def update_enquiry(id):
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    data["updated_at"] = datetime.now()

    try:
        result = enquiries_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": data}
        )
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Enquiry not found"}), 404

    return jsonify({"status": "success", "message": "Enquiry updated"}), 200


@app.route("/api/enquiry/<id>", methods=["DELETE"])
def delete_enquiry(id):
    try:
        result = enquiries_collection.delete_one({"_id": ObjectId(id)})
    except Exception:
        return jsonify({"status": "error", "message": "Invalid ID format"}), 400

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Enquiry not found"}), 404

    return jsonify({"status": "success", "message": "Enquiry deleted"}), 200


# =========================
# MATERIAL API ROUTES (Atlas: materials collection)
# =========================

@app.route("/api/materials", methods=["GET"])
def api_get_materials():
    materials = [serialize_doc(m) for m in materials_collection.find()]
    return jsonify({"status": "success", "data": materials}), 200


@app.route("/api/materials/<material_id>", methods=["GET"])
def api_get_single_material(material_id):
    material = materials_collection.find_one({"id": material_id})

    if not material:
        return jsonify({"status": "error", "message": "Material not found"}), 404

    return jsonify({"status": "success", "data": serialize_doc(material)}), 200


@app.route("/api/materials", methods=["POST"])
def api_add_material():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    def build_material_doc(item):
        material_name = item.get("name", "")
        return {
            "id":          create_material_id(material_name),
            "name":        material_name,
            "category":    item.get("category", ""),
            "description": item.get("description", ""),
            "image":       item.get("image", ""),
            "subtypes":    item.get("subtypes", []),
            "created_at":  datetime.now()
        }

    # Bulk materials from Postman: accepts a JSON list
    if isinstance(data, list):
        inserted_ids = []
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            if not item.get("name"):
                skipped.append({"index": index, "reason": "Material name is required"})
                continue

            material = build_material_doc(item)
            result = materials_collection.insert_one(material)
            inserted_ids.append(str(result.inserted_id))
            log_admin_action("material_added_via_api_bulk", {"name": item.get("name", "")})

        return jsonify({
            "status": "success",
            "message": f"{len(inserted_ids)} materials added successfully",
            "ids": inserted_ids,
            "skipped": skipped
        }), 201

    # Single material
    material_name = data.get("name", "")
    if not material_name:
        return jsonify({"status": "error", "message": "Material name is required"}), 400

    new_material = build_material_doc(data)
    result = materials_collection.insert_one(new_material)
    new_material["_id"] = str(result.inserted_id)

    log_admin_action("material_added_via_api", {"name": material_name})

    return jsonify({
        "status": "success",
        "message": "Material added successfully",
        "data": serialize_doc(new_material)
    }), 201


@app.route("/api/materials/<material_id>", methods=["PUT"])
def api_update_material(material_id):
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    update_data = {
        k: data[k]
        for k in ["name", "category", "description", "image", "subtypes"]
        if k in data and data[k] is not None
    }
    update_data["updated_at"] = datetime.now()

    result = materials_collection.update_one(
        {"id": material_id},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Material not found"}), 404

    updated = serialize_doc(materials_collection.find_one({"id": material_id}))
    log_admin_action("material_updated", {"material_id": material_id})

    return jsonify({
        "status": "success",
        "message": "Material updated successfully",
        "data": updated
    }), 200


@app.route("/api/materials/<material_id>", methods=["PATCH"])
def api_patch_material(material_id):
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    allowed_fields = ["name", "category", "description", "image", "subtypes"]
    patch_data = {k: v for k, v in data.items() if k in allowed_fields}

    if not patch_data:
        return jsonify({"status": "error", "message": "No valid fields to update"}), 400

    patch_data["updated_at"] = datetime.now()

    result = materials_collection.update_one(
        {"id": material_id},
        {"$set": patch_data}
    )

    if result.matched_count == 0:
        return jsonify({"status": "error", "message": "Material not found"}), 404

    updated = serialize_doc(materials_collection.find_one({"id": material_id}))
    return jsonify({
        "status": "success",
        "message": "Material updated partially",
        "data": updated
    }), 200


@app.route("/api/materials/<material_id>", methods=["DELETE"])
def api_delete_material(material_id):
    result = materials_collection.delete_one({"id": material_id})

    if result.deleted_count == 0:
        return jsonify({"status": "error", "message": "Material not found"}), 404

    log_admin_action("material_deleted", {"material_id": material_id})

    return jsonify({
        "status": "success",
        "message": "Material deleted successfully"
    }), 200



# =========================
# CUSTOMER / SETTINGS / CATEGORY / PRODUCT API ROUTES
# Added without changing existing features
# =========================

@app.route("/api/customers", methods=["GET"])
def get_all_customers():
    customers = [serialize_doc(c) for c in customers_collection.find().sort("_id", -1)]
    return jsonify({"status": "success", "data": customers}), 200


@app.route("/api/settings", methods=["GET"])
def get_settings():
    settings = settings_collection.find_one({"type": "company"})
    if not settings:
        default_settings = {
            "type": "company",
            "business_name": "Bhoomi Trading",
            "phone": company.get("phone", ""),
            "email": company.get("email", ""),
            "whatsapp": company.get("whatsapp", ""),
            "created_at": datetime.now()
        }
        settings_collection.insert_one(default_settings)
        settings = default_settings

    return jsonify({"status": "success", "data": serialize_doc(settings)}), 200


@app.route("/api/settings", methods=["POST"])
def update_settings():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    # Bulk settings from Postman: accepts a JSON list
    # Note: settings are usually single company config, but this prevents list errors.
    if isinstance(data, list):
        updated_count = 0
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            item["updated_at"] = datetime.now()
            setting_type = item.get("type", "company")

            settings_collection.update_one(
                {"type": setting_type},
                {
                    "$set": item,
                    "$setOnInsert": {"type": setting_type, "created_at": datetime.now()}
                },
                upsert=True
            )
            updated_count += 1

        log_admin_action("settings_bulk_updated", {"updated_count": updated_count})

        return jsonify({
            "status": "success",
            "message": f"{updated_count} settings records saved successfully",
            "skipped": skipped
        }), 200

    # Single settings object
    data["updated_at"] = datetime.now()
    setting_type = data.get("type", "company")

    settings_collection.update_one(
        {"type": setting_type},
        {
            "$set": data,
            "$setOnInsert": {"type": setting_type, "created_at": datetime.now()}
        },
        upsert=True
    )

    log_admin_action("settings_updated", data)
    settings = serialize_doc(settings_collection.find_one({"type": setting_type}))

    return jsonify({
        "status": "success",
        "message": "Settings saved successfully",
        "data": settings
    }), 200


@app.route("/api/categories", methods=["GET"])
def get_all_categories():
    categories = [serialize_doc(c) for c in categories_collection.find().sort("created_at", -1)]
    return jsonify({"status": "success", "data": categories}), 200


@app.route("/api/categories", methods=["POST"])
def add_category():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    def build_category_doc(item):
        return {
            "category_name": item.get("category_name") or item.get("name"),
            "description": item.get("description", ""),
            "created_at": datetime.now()
        }

    # Bulk categories from Postman: accepts a JSON list
    if isinstance(data, list):
        inserted_ids = []
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            category_name = item.get("category_name") or item.get("name")
            if not category_name:
                skipped.append({"index": index, "reason": "Category name is required"})
                continue

            category = build_category_doc(item)
            result = categories_collection.insert_one(category)
            inserted_ids.append(str(result.inserted_id))
            log_admin_action("category_added_bulk", {"category_name": category_name})

        return jsonify({
            "status": "success",
            "message": f"{len(inserted_ids)} categories added successfully",
            "ids": inserted_ids,
            "skipped": skipped
        }), 201

    # Single category
    category_name = data.get("category_name") or data.get("name")

    if not category_name:
        return jsonify({"status": "error", "message": "Category name is required"}), 400

    new_category = build_category_doc(data)
    result = categories_collection.insert_one(new_category)
    new_category["_id"] = str(result.inserted_id)

    log_admin_action("category_added", {"category_name": category_name})

    return jsonify({
        "status": "success",
        "message": "Category added successfully",
        "data": serialize_doc(new_category)
    }), 201


@app.route("/api/products", methods=["GET"])
def get_all_products():
    products = [serialize_doc(p) for p in products_collection.find().sort("created_at", -1)]
    return jsonify({"status": "success", "data": products}), 200


@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No JSON data received"}), 400

    def build_product_doc(item):
        return {
            "product_name": item.get("product_name") or item.get("name"),
            "category": item.get("category", ""),
            "description": item.get("description", ""),
            "image": item.get("image", ""),
            "price": item.get("price", "As per requirement"),
            "created_at": datetime.now()
        }

    # Bulk products from Postman: accepts a JSON list
    if isinstance(data, list):
        inserted_ids = []
        skipped = []

        for index, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                skipped.append({"index": index, "reason": "Item must be a JSON object"})
                continue

            product_name = item.get("product_name") or item.get("name")
            if not product_name:
                skipped.append({"index": index, "reason": "Product name is required"})
                continue

            product = build_product_doc(item)
            result = products_collection.insert_one(product)
            inserted_ids.append(str(result.inserted_id))
            log_admin_action("product_added_bulk", {"product_name": product_name})

        return jsonify({
            "status": "success",
            "message": f"{len(inserted_ids)} products added successfully",
            "ids": inserted_ids,
            "skipped": skipped
        }), 201

    # Single product
    product_name = data.get("product_name") or data.get("name")

    if not product_name:
        return jsonify({"status": "error", "message": "Product name is required"}), 400

    new_product = build_product_doc(data)
    result = products_collection.insert_one(new_product)
    new_product["_id"] = str(result.inserted_id)

    log_admin_action("product_added", {"product_name": product_name})

    return jsonify({
        "status": "success",
        "message": "Product added successfully",
        "data": serialize_doc(new_product)
    }), 201


# =========================
# ADMIN LOGS API (read-only)
# =========================

@app.route("/api/admin/logs", methods=["GET"])
def get_admin_logs():
    if not session.get("admin_logged_in"):
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    logs = [serialize_doc(l) for l in admin_logs_collection.find().sort("timestamp", -1).limit(100)]
    return jsonify({"status": "success", "data": logs}), 200


# =========================
# HEALTH CHECK / TEST ROUTE
# =========================

@app.route("/health", methods=["GET"])
def health_check():
    try:
        mongo_client.admin.command("ping")
        status = "connected"
    except Exception as e:
        status = f"error: {e}"

    return jsonify({
        "status": "ok",
        "mongodb": status,
        "database": db.name,
        "collections": {
            "enquiries":  enquiries_collection.count_documents({}),
            "materials":  materials_collection.count_documents({}),
            "users":      users_collection.count_documents({}),
            "customers":  customers_collection.count_documents({}),
            "settings":   settings_collection.count_documents({}),
            "categories": categories_collection.count_documents({}),
            "products":   products_collection.count_documents({}),
            "admin_logs": admin_logs_collection.count_documents({})
        }
    }), 200

#######
@app.route("/import-materials", methods=["GET"])
def import_materials():
    materials_file = os.path.join(BASE_DIR, "data", "materials.json")

    if not os.path.exists(materials_file):
        return jsonify({
            "status": "error",
            "message": f"File not found: {materials_file}"
        }), 404

    with open(materials_file, "r", encoding="utf-8") as file:
        materials = json.load(file)

    materials_collection.delete_many({})

    if materials:
        materials_collection.insert_many(materials)

    return jsonify({
        "status": "success",
        "message": "Old materials imported to MongoDB",
        "total": len(materials)
    })
########test#
@app.route("/clean-customers")
def clean_customers():
    customers_collection.update_many(
        {},
        {
            "$unset": {
                "last_material_enquired": "",
                "last_message": "",
                "last_enquiry_at": "",
                "source": "",
                "created_at": "",
                "updated_at": ""
            }
        }
    )

    return "Customers collection cleaned successfully"

    #####
    from dotenv import load_dotenv
    import os
        
    load_dotenv()

    MONGO_URI = os.getenv("MONGO_URI")    #####
# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)