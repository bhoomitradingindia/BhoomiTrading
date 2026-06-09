# Bhoomi Trading – Website

A professional, fully responsive Flask website for Bhoomi Trading,
a Mumbai-based retailer and supplier of bag-making and purse-making materials.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run development server
python app.py
```

Open http://localhost:5000 in your browser.

---

## Project Structure

```
bhoomi_trading/
├── app.py                  ← Flask routes
├── requirements.txt
├── data/
│   ├── __init__.py
│   └── products.py         ← ALL business data lives here
├── templates/
│   ├── base.html           ← Navigation, footer, WhatsApp button
│   ├── home.html
│   ├── services.html
│   ├── catalogue.html
│   └── contact.html
└── static/
    ├── css/
    │   └── main.css
    └── js/
        └── main.js
```

---

## How to Update Business Data

All editable content is in **`data/products.py`**:

### Update contact details
Edit the `COMPANY_INFO` dict — phone, email, WhatsApp number, address.

### Add a new material category
Append to `PRODUCTS`:
```python
{
    "id": "accessories",          # url-safe, no spaces
    "name": "Bag Accessories",
    "icon": "🔩",
    "color_accent": "#7A6652",   # card accent colour
    "description": "Zippers, buckles, rivets and more.",
    "materials": [
        {"name": "Metal Zippers",   "description": "YKK compatible"},
        {"name": "Plastic Buckles", "description": "Side-release style"},
    ],
},
```

### Add a sub-material to an existing category
Find the category in `PRODUCTS` and append to its `"materials"` list:
```python
{"name": "New Material Name", "description": "Optional description"},
```

### Add a service
Append to `SERVICES` in `products.py`:
```python
{
    "id": "unique_id",
    "title": "Service Title",
    "icon": "🎯",
    "description": "Full description of the service.",
    "highlights": ["Point 1", "Point 2", "Point 3"],
},
```

---

## WhatsApp Integration

All WhatsApp links use the `wa.me` deep-link format:
```
https://wa.me/{PHONE}?text={URL_ENCODED_MESSAGE}
```

- **Floating button**: generic enquiry message
- **Catalogue items**: pre-fills "Hello Bhoomi Trading, I am interested in [Material Name]. Please share details."
- **Services**: pre-fills the service name

Update `COMPANY_INFO["whatsapp"]` with the real number (country code + number, no `+`).

---

## Deployment

For production, use Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Or set the `FLASK_ENV` environment variable:
```bash
export FLASK_ENV=production
```
