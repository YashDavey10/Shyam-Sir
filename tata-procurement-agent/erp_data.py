"""
ERP Knowledge Base & Static Cache for Tata Motors Pune Manufacturing Plant (TMPVL & TPEML)
"""

import copy

INITIAL_MATERIALS = {
    "TML-PV-101": {
        "code": "TML-PV-101",
        "name": "ABS Wheel Speed Sensor",
        "primary_supplier": "SUP-01",
        "primary_price": 580.0,
        "alt_supplier": "SUP-02",
        "alt_price": 625.0,
        "pli_critical": False,
        "category": "Powertrain / Safety",
        "unit": "units"
    },
    "TML-EV-303": {
        "code": "TML-EV-303",
        "name": "EV Battery Thermal Paste",
        "primary_supplier": "SUP-05",
        "primary_price": 36500.0,
        "alt_supplier": "SUP-06",
        "alt_price": 29000.0,
        "pli_critical": True,
        "category": "EV Battery Pack",
        "unit": "pails"
    },
    "TML-BIW-404": {
        "code": "TML-BIW-404",
        "name": "Weld Electrode Cap",
        "primary_supplier": "SUP-07",
        "primary_price": 13800.0,
        "alt_supplier": "SUP-08",
        "alt_price": 14900.0,
        "pli_critical": False,
        "category": "BIW Body Framing",
        "unit": "boxes"
    },
    "TML-PNT-505": {
        "code": "TML-PNT-505",
        "name": "CED Primer",
        "primary_supplier": "SUP-09",
        "primary_price": 79000.0,
        "alt_supplier": "SUP-10",
        "alt_price": 82500.0,
        "pli_critical": False,
        "category": "Paint Shop Electrodip",
        "unit": "drums"
    },
    "TML-ELE-707": {
        "code": "TML-ELE-707",
        "name": "12V 120A Alternator",
        "primary_supplier": "SUP-ARIBA",
        "primary_price": 4200.0,
        "spot_price": 4200.0,
        "alt_supplier": None,
        "alt_price": 4200.0,
        "pli_critical": False,
        "ariba_discount_threshold": 1500,
        "ariba_discount_pct": 5.0,
        "category": "Electrical Assembly",
        "unit": "units"
    },
    "TML-IT-808": {
        "code": "TML-IT-808",
        "name": "10.25\" Display",
        "primary_supplier": "SUP-ARIBA",
        "primary_price": 18000.0,
        "spot_price": 18000.0,
        "alt_supplier": None,
        "alt_price": 18000.0,
        "pli_critical": False,
        "category": "Infotainment",
        "unit": "units"
    }
}

INITIAL_SUPPLIERS = {
    "SUP-01": {
        "id": "SUP-01",
        "name": "Bosch",
        "email": "orders.automotive@bosch.com",
        "contact_person": "Rajesh Sharma (Key Account Lead)",
        "location": "Nashik",
        "lead_days": 7,
        "moq": 500,
        "status": "Active",
        "ppm": 11,
        "pli_eligible": True
    },
    "SUP-02": {
        "id": "SUP-02",
        "name": "Uno Minda",
        "email": "dispatch.pune@unominda.com",
        "contact_person": "Amit Kulkarni (JIT Operations)",
        "location": "Pune Local",
        "lead_days": 1,
        "moq": 100,
        "status": "Active",
        "ppm": 24,
        "pli_eligible": True
    },
    "SUP-05": {
        "id": "SUP-05",
        "name": "Henkel India",
        "email": "industrial.adhesives@henkel.com",
        "contact_person": "Priya Nair (OEM Adhesives)",
        "location": "Pune",
        "lead_days": 4,
        "moq": 5,
        "status": "Active",
        "ppm": 14,
        "pli_eligible": True
    },
    "SUP-06": {
        "id": "SUP-06",
        "name": "Shenzhen Tech",
        "email": "export.battery@shenzhentech.cn",
        "contact_person": "Chen Wei (Global Sales)",
        "location": "China",
        "lead_days": 21,
        "moq": 20,
        "status": "Unverified",
        "ppm": 390,
        "pli_eligible": False
    },
    "SUP-07": {
        "id": "SUP-07",
        "name": "ITW India",
        "email": "welding.orders@itwindia.com",
        "contact_person": "Sandeep Reddy (BIW Welding Lead)",
        "location": "Hyderabad",
        "lead_days": 6,
        "moq": 10,
        "status": "Active",
        "ppm": 32,
        "pli_eligible": True
    },
    "SUP-08": {
        "id": "SUP-08",
        "name": "Panasonic Welding India",
        "email": "sales.welding@panasonic.in",
        "contact_person": "Vikram Joshi",
        "location": "Gurugram",
        "lead_days": 3,
        "moq": 15,
        "status": "Active",
        "ppm": 45,
        "pli_eligible": True
    },
    "SUP-09": {
        "id": "SUP-09",
        "name": "Kansai Nerolac",
        "email": "industrial.coatings@nerolac.com",
        "contact_person": "Quality & OEM Desk",
        "location": "Lote",
        "lead_days": 4,
        "moq": 5,
        "status": "QUALITY HOLD",
        "ppm": 680,
        "pli_eligible": True
    },
    "SUP-10": {
        "id": "SUP-10",
        "name": "PPG Asian Paints",
        "email": "auto.coatings.pune@ppgasianpaints.com",
        "contact_person": "Sunil Deshmukh (Paint OEM)",
        "location": "Pune",
        "lead_days": 2,
        "moq": 4,
        "status": "Active",
        "ppm": 21,
        "pli_eligible": True
    },
    "SUP-ARIBA": {
        "id": "SUP-ARIBA",
        "name": "SAP Ariba Contracted Vendor (Lucas-TVS / Denso)",
        "email": "ariba.auto-orders@lucastvs.com",
        "contact_person": "Centralized Sourcing Desk",
        "location": "Pune Auto Cluster",
        "lead_days": 2,
        "moq": 100,
        "status": "Active",
        "ppm": 18,
        "pli_eligible": True
    }
}

INITIAL_COST_CENTERS = {
    "CC-PU-TCF": {
        "code": "CC-PU-TCF",
        "name": "Trim, Chassis & Final (TCF)",
        "total_budget": 3400000.0,
        "remaining_budget": 3400000.0,
        "tier1_limit": 400000.0,    # Auto-approve <= 4L
        "tier2_limit": 1500000.0,   # Shop Head <= 15L
        # Tier 3 Finance > 15L
    },
    "CC-PU-BIW": {
        "code": "CC-PU-BIW",
        "name": "Body-in-White (BIW)",
        "total_budget": 920000.0,
        "remaining_budget": 920000.0,
        "tier1_limit": 200000.0,    # Auto-approve <= 2L
        "tier2_limit": 600000.0,    # Shop Head <= 6L
        # Tier 3 Finance > 6L
    },
    "CC-PU-PAINT": {
        "code": "CC-PU-PAINT",
        "name": "Paint Shop",
        "total_budget": 1550000.0,
        "remaining_budget": 1550000.0,
        "tier1_limit": 300000.0,    # Auto-approve <= 3L
        "tier2_limit": 1000000.0,   # Shop Head <= 10L
        # Tier 3 Finance > 10L
    }
}


class ERPDatabase:
    """Live In-Memory ERP Backend with Reset and Transactional Commits"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.materials = copy.deepcopy(INITIAL_MATERIALS)
        self.suppliers = copy.deepcopy(INITIAL_SUPPLIERS)
        self.cost_centers = copy.deepcopy(INITIAL_COST_CENTERS)
        self.pr_history = []  # Tracks last 48 hours for anti-split detection
        self.po_records = []  # Dispatched / Staged POs
        self.email_outbox = [] # Autonomous Dispatched Emails

    def get_material(self, code_or_name):
        if not code_or_name:
            return None
        code_or_name = str(code_or_name).upper().strip()
        if code_or_name in self.materials:
            return self.materials[code_or_name]
        
        # Search by partial name or keyword
        for mat in self.materials.values():
            if code_or_name in mat["name"].upper() or code_or_name in mat["code"].upper():
                return mat
        return None

    def get_supplier(self, sup_id):
        if not sup_id:
            return None
        return self.suppliers.get(sup_id)

    def get_cost_center(self, cc_code):
        if not cc_code:
            return None
        return self.cost_centers.get(cc_code)

    def deduct_budget(self, cc_code, amount):
        cc = self.cost_centers.get(cc_code)
        if cc and cc["remaining_budget"] >= amount:
            cc["remaining_budget"] -= amount
            return True
        return False

    def to_dict(self):
        return {
            "materials": self.materials,
            "suppliers": self.suppliers,
            "cost_centers": self.cost_centers,
            "history_count": len(self.pr_history),
            "po_count": len(self.po_records),
            "email_count": len(self.email_outbox)
        }


# Singleton live ERP instance
erp_db = ERPDatabase()
