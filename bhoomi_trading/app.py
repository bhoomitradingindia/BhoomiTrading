import os
import json
from datetime import datetime

from flask import Flask, render_template, request, redirect, jsonify
import gspread
from google.oauth2.service_account import Credentials


app = Flask(__name__)

# =========================
# BASE PATHS
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "data", "materials.json")
ENQUIRY_FILE = os.path.join(BASE_DIR, "data", "enquiries.json")

# Google service account JSON file
CREDS_FILE = os.path.join(BASE_DIR, "enq_logs.json")

# Google Sheet name
GOOGLE_SHEET_NAME = "Bhoomi Trading Enquiries"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


# =========================
# COMPANY DATA
# =========================

company = {
    "established": "2026",
    "tagline": "Quality Materials for Bags, Purses & Creative Designs",
    "description": "Bhoomi Trading supplies quality bag-making materials including Rexine, Leather, Canvas, Nylon Fabric and Polyester Fabric.",
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

def load_json_file(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json_file(file_path, data):
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def load_materials():
    return load_json_file(DATA_FILE, [])


def save_materials(materials):
    save_json_file(DATA_FILE, materials)


def load_enquiries():
    return load_json_file(ENQUIRY_FILE, [])


def save_enquiry(data):
    enquiries = load_enquiries()
    enquiries.append(data)
    save_json_file(ENQUIRY_FILE, enquiries)


def save_enquiry_to_google_sheet(data):
    creds = Credentials.from_service_account_file(
        CREDS_FILE,
        scopes=SCOPES
    )

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


def create_material_id(name):
    return name.lower().strip().replace(" ", "-")


# =========================
# PAGE ROUTES
# =========================

@app.route("/")
def home():
    materials = load_materials()
    featured = materials[:4]
    return render_template("home.html", company=company, featured=featured)


@app.route("/catalogue")
def catalogue():
    materials = load_materials()
    return render_template("catalogue.html", company=company, materials=materials)


@app.route("/services")
def services():
    return render_template("services.html", company=company, services=services_data)


@app.route("/contact")
def contact():
    return render_template("contact.html", company=company)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    materials = load_materials()

    if request.method == "POST":
        subtypes = request.form["subtypes"].split(",")

        new_material = {
            "id": create_material_id(request.form["name"]),
            "name": request.form["name"],
            "category": request.form["category"],
            "description": request.form["description"],
            "image": request.form["image"],
            "subtypes": [item.strip() for item in subtypes]
        }

        materials.append(new_material)
        save_materials(materials)

        return redirect("/admin")

    return render_template("admin.html", company=company, materials=materials)


# =========================
# WEBSITE ENQUIRY FORM ROUTE
# =========================

@app.route("/enquiry", methods=["POST"])
def enquiry():
    enquiry_data = {
        "name": request.form.get("name", ""),
        "phone": request.form.get("phone", ""),
        "email": request.form.get("email", ""),
        "material": request.form.get("material", ""),
        "message": request.form.get("message", "")
    }

    try:
        save_enquiry(enquiry_data)
        save_enquiry_to_google_sheet(enquiry_data)
        print("New Website Enquiry:", enquiry_data)

    except Exception as e:
        print("Website enquiry error:", e)

    return redirect("/contact")


# =========================
# ENQUIRY API ROUTES
# =========================

@app.route("/api/enquiry", methods=["GET"])
def api_get_enquiries():
    enquiries = load_enquiries()

    return jsonify({
        "status": "success",
        "data": enquiries
    })


@app.route("/api/enquiry", methods=["POST","DELETE"])
def api_add_enquiry():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    try:
        if isinstance(data, list):
            for item in data:
                save_enquiry(item)
                save_enquiry_to_google_sheet(item)

            return jsonify({
                "status": "success",
                "message": "Multiple enquiries saved successfully",
                "total": len(data)
            }), 201

        save_enquiry(data)
        save_enquiry_to_google_sheet(data)

        return jsonify({
            "status": "success",
            "message": "Enquiry saved successfully",
            "data": data
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# =========================
# MATERIAL API ROUTES
# =========================

@app.route("/api/materials", methods=["GET"])
def api_get_materials():
    materials = load_materials()

    return jsonify({
        "status": "success",
        "data": materials
    })


@app.route("/api/materials/<material_id>", methods=["GET"])
def api_get_single_material(material_id):
    materials = load_materials()

    for material in materials:
        if material.get("id") == material_id:
            return jsonify({
                "status": "success",
                "data": material
            })

    return jsonify({
        "status": "error",
        "message": "Material not found"
    }), 404


@app.route("/api/materials", methods=["POST"])
def api_add_material():
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    materials = load_materials()

    material_name = data.get("name", "")

    if not material_name:
        return jsonify({
            "status": "error",
            "message": "Material name is required"
        }), 400

    new_material = {
        "id": create_material_id(material_name),
        "name": material_name,
        "category": data.get("category", ""),
        "description": data.get("description", ""),
        "image": data.get("image", ""),
        "subtypes": data.get("subtypes", [])
    }

    materials.append(new_material)
    save_materials(materials)

    return jsonify({
        "status": "success",
        "message": "Material added successfully",
        "data": new_material
    }), 201


@app.route("/api/materials/<material_id>", methods=["PUT"])
def api_update_material(material_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    materials = load_materials()

    for material in materials:
        if material.get("id") == material_id:
            material["name"] = data.get("name", material.get("name"))
            material["category"] = data.get("category", material.get("category"))
            material["description"] = data.get("description", material.get("description"))
            material["image"] = data.get("image", material.get("image"))
            material["subtypes"] = data.get("subtypes", material.get("subtypes"))

            save_materials(materials)

            return jsonify({
                "status": "success",
                "message": "Material updated successfully",
                "data": material
            })

    return jsonify({
        "status": "error",
        "message": "Material not found"
    }), 404


@app.route("/api/materials/<material_id>", methods=["PATCH"])
def api_patch_material(material_id):
    data = request.get_json()

    if not data:
        return jsonify({
            "status": "error",
            "message": "No JSON data received"
        }), 400

    materials = load_materials()

    for material in materials:
        if material.get("id") == material_id:
            allowed_fields = ["name", "category", "description", "image", "subtypes"]

            for key, value in data.items():
                if key in allowed_fields:
                    material[key] = value

            save_materials(materials)

            return jsonify({
                "status": "success",
                "message": "Material updated partially",
                "data": material
            })

    return jsonify({
        "status": "error",
        "message": "Material not found"
    }), 404


@app.route("/api/materials/<material_id>", methods=["DELETE"])
def api_delete_material(material_id):
    materials = load_materials()

    updated_materials = [
        material for material in materials
        if material.get("id") != material_id
    ]

    if len(updated_materials) == len(materials):
        return jsonify({
            "status": "error",
            "message": "Material not found"
        }), 404

    save_materials(updated_materials)

    return jsonify({
        "status": "success",
        "message": "Material deleted successfully"
    })


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)