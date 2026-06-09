import os
import json
from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "materials.json")

company = {
    "phone": "+91 9876543210",
    "email": "bhoomitradingindia@gmail.com",
    "whatsapp": "919876543210"
}

def load_materials():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

def save_materials(materials):
    with open(DATA_FILE, "w") as file:
        json.dump(materials, file, indent=4)

@app.route("/")
def home():
    return render_template("home.html", company=company)

@app.route("/catalogue")
def catalogue():
    materials = load_materials()
    return render_template("catalogue.html", company=company, materials=materials)

@app.route("/services")
def services():
    return render_template("services.html", company=company)

@app.route("/contact")
def contact():
    return render_template("contact.html", company=company)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    materials = load_materials()

    if request.method == "POST":
        new_material = {
            "id": request.form["name"].lower().replace(" ", "-"),
            "name": request.form["name"],
            "category": request.form["category"],
            "description": request.form["description"],
            "image": request.form["image"],
            "subtypes": request.form["subtypes"].split(",")
        }

        materials.append(new_material)
        save_materials(materials)
        return redirect("/admin")

    return render_template("admin.html", materials=materials)

if __name__ == "__main__":
    app.run(debug=True)