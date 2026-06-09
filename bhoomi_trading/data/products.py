"""
data/products.py
────────────────
Central data store for Bhoomi Trading.

HOW TO ADD A NEW CATEGORY:
  Append a new dict to PRODUCTS following the existing schema.

HOW TO ADD A SUB-MATERIAL:
  Append to the "materials" list inside the relevant category dict.
  Each sub-material only needs a "name" and optional "description".
"""

# ─────────────────────────────────────────────────────────────
# Company Information
# ─────────────────────────────────────────────────────────────
COMPANY_INFO = {
    "name": "Bhoomi Trading",
    "tagline": "Quality Materials for Bags, Purses & Creative Designs",
    "phone": "+91 98765 43210",       # ← update with real number
    "email": "info@bhoomitrading.com", # ← update with real email
    "whatsapp": "919876543210",        # ← country code + number, no +
    "address": "Shop No. 12, Dharavi Industrial Area, Mumbai, Maharashtra 400017",
    "maps_url": "https://maps.google.com/?q=Dharavi+Industrial+Area+Mumbai",
    "established": "2005",
    "description": (
        "Bhoomi Trading has been a trusted name in the bag and purse "
        "material supply industry for nearly two decades. We source and "
        "supply premium Rexine, genuine and synthetic Leather, Canvas, "
        "Nylon, Polyester Fabric, and all related accessories — "
        "serving craftsmen, boutiques, manufacturers, and wholesalers "
        "across India."
    ),
}

# ─────────────────────────────────────────────────────────────
# Product Catalogue
# Each category:
#   id          – url-safe unique key
#   name        – display name
#   icon        – SVG path or emoji used in the card
#   description – one-liner shown on the catalogue card
#   materials   – list of sub-materials
#     name        – display name (used in WhatsApp message)
#     description – optional detail line
# ─────────────────────────────────────────────────────────────
PRODUCTS = [
    {
        "id": "rexine",
        "name": "Rexine",
        "icon": "🪡",
        "color_accent": "#8B4513",
        "description": "Durable synthetic leather available in dozens of textures and finishes. Ideal for bags, wallets, and upholstery.",
        "materials": [
            {"name": "Plain Rexine",    "description": "Smooth, uniform surface — available in 40+ colours"},
            {"name": "Printed Rexine",  "description": "Vibrant patterns printed on high-grade base material"},
            {"name": "Foam Rexine",     "description": "Cushioned backing for soft-touch products"},
            {"name": "Glossy Rexine",   "description": "High-shine finish for premium fashion accessories"},
            {"name": "Matte Rexine",    "description": "Sophisticated, non-reflective surface"},
            {"name": "Embossed Rexine", "description": "Textured surface mimicking crocodile, snake, or lychee grain"},
        ],
    },
    {
        "id": "leather",
        "name": "Leather",
        "icon": "🧳",
        "color_accent": "#6B3A2A",
        "description": "Genuine and synthetic leather hides in full-grain, top-grain, and split varieties for all applications.",
        "materials": [
            {"name": "Full Grain Leather",     "description": "Highest quality, natural texture retained"},
            {"name": "Top Grain Leather",      "description": "Sanded for uniformity, most popular choice"},
            {"name": "Split Leather",          "description": "Cost-effective option for inner linings"},
            {"name": "PU Leather",             "description": "Polyurethane coated — vegan-friendly alternative"},
            {"name": "Nubuck Leather",         "description": "Buffed outer grain for a suede-like feel"},
            {"name": "Patent Leather",         "description": "Lacquer finish for high-gloss formal items"},
        ],
    },
    {
        "id": "canvas",
        "name": "Canvas",
        "icon": "🎨",
        "color_accent": "#A0785A",
        "description": "Heavy-duty woven fabric, preferred for tote bags, backpacks, and outdoor utility bags.",
        "materials": [
            {"name": "Plain Canvas",          "description": "Natural, undyed — perfect for customisation"},
            {"name": "Waxed Canvas",          "description": "Water-resistant coating for outdoor durability"},
            {"name": "Duck Canvas",           "description": "Tightly woven, heavy-weight for load-bearing bags"},
            {"name": "Printed Canvas",        "description": "Screen or digital-printed designs available"},
            {"name": "Cotton Canvas",         "description": "Soft and breathable, ideal for fashion totes"},
            {"name": "Poly-Cotton Canvas",    "description": "Blended for added strength and colour retention"},
        ],
    },
    {
        "id": "nylon",
        "name": "Nylon Fabric",
        "icon": "🧵",
        "color_accent": "#4A6741",
        "description": "Lightweight, tear-resistant nylon in various deniers for travel bags, backpacks, and sports gear.",
        "materials": [
            {"name": "420D Nylon",         "description": "Medium-weight, versatile everyday bag material"},
            {"name": "600D Nylon",         "description": "Heavier denier for structured school and travel bags"},
            {"name": "1680D Ballistic Nylon", "description": "Military-grade durability for heavy-duty luggage"},
            {"name": "Ripstop Nylon",      "description": "Grid-reinforced to prevent tear propagation"},
            {"name": "Nylon Oxford",       "description": "Plain-woven, water-repellent finish"},
            {"name": "Nylon Taslan",       "description": "Textured surface, highly abrasion-resistant"},
        ],
    },
    {
        "id": "polyester",
        "name": "Polyester Fabric",
        "icon": "🏷️",
        "color_accent": "#3A5F7D",
        "description": "Affordable, colourfast polyester fabric in multiple weaves — the backbone of mass-market bag production.",
        "materials": [
            {"name": "300D Polyester",         "description": "Lightweight and cost-effective for small pouches"},
            {"name": "600D Polyester",         "description": "Popular mid-range for school bags and totes"},
            {"name": "900D Polyester",         "description": "Heavy duty — backpacks and laptop bags"},
            {"name": "Polyester Oxford",       "description": "Woven finish with water-resistant coating"},
            {"name": "Polyester Taffeta",      "description": "Smooth lining fabric for interiors"},
            {"name": "Jacquard Polyester",     "description": "Woven patterns for decorative and fashion use"},
        ],
    },
    # ── Add more categories below this line ──
    # {
    #     "id": "accessories",
    #     "name": "Bag Accessories",
    #     "icon": "🔩",
    #     "color_accent": "#7A6652",
    #     "description": "Zippers, buckles, D-rings, rivets, and more.",
    #     "materials": [
    #         {"name": "Metal Zippers",   "description": "YKK and compatible brands"},
    #         {"name": "Plastic Buckles", "description": "Side-release and ladder-lock styles"},
    #     ],
    # },
]

# ─────────────────────────────────────────────────────────────
# Services
# ─────────────────────────────────────────────────────────────
SERVICES = [
    {
        "id": "material_supply",
        "title": "Material Supply",
        "icon": "📦",
        "description": (
            "We supply a comprehensive range of bag-making materials — "
            "Rexine, Leather, Canvas, Nylon, and Polyester — sourced "
            "from trusted manufacturers across India and abroad."
        ),
        "highlights": ["Pan-India delivery", "Consistent quality batches", "Minimum order flexibility"],
    },
    {
        "id": "retail",
        "title": "Retail Orders",
        "icon": "🛍️",
        "description": (
            "Craftsmen, home-based designers, and small studios can "
            "purchase materials in small quantities with no minimum "
            "order constraint — perfect for prototyping and bespoke work."
        ),
        "highlights": ["No minimum order", "Walk-in & online enquiry", "Sample swatches available"],
    },
    {
        "id": "wholesale",
        "title": "Wholesale Orders",
        "icon": "🏭",
        "description": (
            "Manufacturers and large retailers benefit from our bulk "
            "pricing tiers, priority stock allocation, and dedicated "
            "account management for repeat orders."
        ),
        "highlights": ["Volume discounts", "Priority dispatch", "Dedicated account manager"],
    },
    {
        "id": "custom_sourcing",
        "title": "Custom Material Sourcing",
        "icon": "🔍",
        "description": (
            "Can't find what you need in our standard catalogue? Share "
            "your specifications — colour, finish, weight, texture — "
            "and we'll source it for you from our supplier network."
        ),
        "highlights": ["Bespoke colour matching", "Custom texture & finish", "Pantone & sample matching"],
    },
]
