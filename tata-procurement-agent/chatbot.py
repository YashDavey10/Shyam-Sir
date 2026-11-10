"""
Procurement Copilot & AI Explanation Engine for Tata Motors Pune Plant (TMPVL & TPEML)
Provides plain-English explanations of autonomous decisions, guardrails, math formulas,
and regulatory compliance logic.
"""

from erp_data import erp_db


class ProcurementChatbot:
    def __init__(self, db=None):
        self.db = db or erp_db

    def reply(self, user_message, context=None):
        """
        Generates an authoritative, conversational explanation based on the user's question,
        current ERP state, and the latest processed PR context.
        """
        msg = user_message.lower().strip()
        last_po = self.db.po_records[-1] if self.db.po_records else None
        last_json = context.get("last_json") if context else None

        # 1. Questions about Supplier Emails / Outbox / Automated Dispatch
        if any(w in msg for w in ["email", "mail", "outbox", "sent", "recipient", "letterhead", "notification"]):
            outbox = self.db.email_outbox
            if not outbox:
                return (
                    "**Autonomous Supplier Email Dispatch System:**\n\n"
                    "The agent is configured to autonomously generate and transmit official Purchase Order emails to verified supplier contact addresses "
                    "immediately upon PO creation.\n\n"
                    "• **Configured Vendor Contacts:**\n"
                    "  - **Uno Minda (`SUP-02`):** `dispatch.pune@unominda.com` (JIT Operations)\n"
                    "  - **Henkel India (`SUP-05`):** `industrial.adhesives@henkel.com` (OEM Adhesives)\n"
                    "  - **PPG Asian Paints (`SUP-10`):** `auto.coatings.pune@ppgasianpaints.com` (Paint OEM)\n"
                    "  - **ITW India (`SUP-07`):** `welding.orders@itwindia.com` (BIW Welding Lead)\n"
                    "  - **Ariba Lucas-TVS (`SUP-ARIBA`):** `ariba.auto-orders@lucastvs.com` (Central Sourcing)\n\n"
                    "Every automated email includes official Tata Motors Pune Plant letterhead, order quantities, delivery gate assignments (Gate #2, #3, or #4), "
                    "contracted rates, and mandatory IATF-16949 Certificate of Analysis (CoA) quality instructions."
                )
            
            # Find matching email if specific supplier mentioned
            target_email = outbox[0]
            for em in outbox:
                if any(k in msg for k in [em["supplier_name"].lower(), em["supplier_id"].lower(), em["material_code"].lower()]):
                    target_email = em
                    break

            return (
                f"**Autonomous Supplier Email Dispatched ({len(outbox)} Total Sent):**\n\n"
                f"• **Supplier:** {target_email['supplier_name']} ({target_email['supplier_id']})\n"
                f"• **Recipient:** {target_email['contact_person']} <`{target_email['recipient_email']}`>\n"
                f"• **Subject:** `{target_email['subject']}`\n"
                f"• **Order Quantity:** {target_email['quantity']} units of `{target_email['material_code']}`\n"
                f"• **Total Value:** ₹{target_email['total_value_inr']:,.2f}\n"
                f"• **Transmission Status:** `{target_email['status']}`\n"
                f"• **Mandatory Logistics:** Gate entry assigned to Tata Motors Pune Plant with required IATF-16949 Certificate of Analysis (CoA).\n\n"
                "You can inspect the full rendered HTML letterhead under the **'Supplier Email Hub'** tab in the top dashboard."
            )

        # 2. Questions about Shenzhen Tech / PLI / Chinese EV parts
        if any(w in msg for w in ["shenzhen", "pli", "china", "foreign", "paste", "303"]):
            return (
                "**Regulatory Guardrail Explanation (Auto PLI Scheme & Quality Gate):**\n\n"
                "• **Why Shenzhen Tech was blocked:** Material `TML-EV-303` (EV Battery Thermal Paste) is classified as **PLI Critical: Yes**. "
                "Under the Ministry of Heavy Industries Auto PLI Scheme, Tata Passenger Electric Mobility Ltd (TPEML) is legally mandated to maintain "
                "a minimum of **50% Domestic Value Addition (DVA)** across EV models (Nexon EV, Punch EV, Curvv EV). Importing uncertified cells or thermal paste "
                "risks catastrophic cancellation and clawback of **₹ hundreds of crores in government subsidies**.\n\n"
                "• **Quality Breach:** Furthermore, Shenzhen Tech (`SUP-06`) is unverified with a defect rate of **390 PPM**, violating our **IATF-16949 ceiling of 100 PPM**.\n\n"
                "• **Automated Action:** The agent executed a mandatory hard block on Shenzhen Tech and rerouted procurement to domestic supplier **Henkel India (Pune)** "
                "at ₹36,500/pail (Lead: 4 Days, 14 PPM, 100% PLI Compliant). Because the order of ₹7,30,000 exceeds TCF's Tier 1 limit (₹4 Lakh), it was escalated to Tier 2 (Shop Head)."
            )

        # 2. Questions about Uno Minda vs Bosch / JIT Emergency Pivot / 10% premium
        if any(w in msg for w in ["minda", "bosch", "jit", "pivot", "sensor", "101", "24 hrs", "premium"]):
            return (
                "**JIT Emergency Logistics & Mathematical Proof:**\n\n"
                "• **Operational Constraint:** The assembly line reported a 24-hour stock-out risk for ABS Sensors (`TML-PV-101`). "
                "Primary supplier **Bosch (`SUP-01`)** has a 7-day lead time and an MOQ of 500 units, making on-time JIT delivery physically impossible.\n\n"
                "• **The JIT Pivot Rule:** The agent evaluates alternate suppliers who can deliver within the emergency window. Local supplier **Uno Minda (`SUP-02`)** in Pune "
                "delivers in 1 day with an MOQ of 100 units.\n\n"
                "• **The 10% Premium Math:**\n"
                "  $$\\Delta P = \\frac{₹625 - ₹580}{₹580} \\times 100 = \\mathbf{+7.76\\%}$$\n"
                "  Since $+7.76\\% \\le 10.0\\%$ (our maximum allowable emergency premium ceiling), the financial guardrail passed.\n\n"
                "• **Economic Justification:** Paying a ₹18,000 premium on 400 sensors saved the plant from a line stoppage that costs **₹15 Lakh to ₹22 Lakh per hour**. "
                "Total PO value of **₹2,50,000** was automatically approved under the TCF Tier 1 limit of ₹4 Lakh."
            )

        # 3. Questions about Kansai Nerolac / Paint / CED Primer / Quality Hold
        if any(w in msg for w in ["kansai", "nerolac", "paint", "ced", "primer", "505", "quality hold", "ppm"]):
            return (
                "**IATF-16949 Quality Gate & Defect Prevention:**\n\n"
                "• **Why Kansai Nerolac was blocked:** `SUP-09` (Kansai Nerolac) is flagged in the ERP backend under **QUALITY HOLD** with an unacceptable defect rating of **680 PPM** "
                "(the IATF-16949 ceiling is 100 PPM). Allowing high-PPM primer into the Cathodic Electrodeposition (CED) dip tank causes cathodic blistering, line shutdown, and paint peeling warranty claims.\n\n"
                "• **Autonomous Rerouting:** Sourcing was automatically redirected to pre-approved alternate **PPG Asian Paints (`SUP-10`)** in Pune (Lead: 2 Days, Active, 21 PPM, MOQ: 4 drums).\n\n"
                "• **Financial Routing:** 10 drums at ₹82,500 = **₹8,25,000**. While ₹8,25,000 exceeds the Paint Shop's Tier 1 auto-approval ceiling of ₹3,00,000, it falls within the Tier 2 band (up to ₹10 Lakh). "
                "The PO was pre-configured and escalated to the **Paint Shop Head** with the quality audit trail attached."
            )

        # 4. Questions about Anti-Split / Weld Caps / Body-in-White
        if any(w in msg for w in ["split", "anti-split", "weld", "cap", "404", "biw", "electrode"]):
            return (
                "**Anti-Split PR Heuristic & Governance Enforcement:**\n\n"
                "• **The Loophole Addressed:** Maintenance engineers often split high-value requisitions into smaller batches to keep each requisition under their Cost Center's Tier 1 auto-approval limit "
                "(₹2,00,000 in Body-in-White), thus bypassing Shop Head supervision.\n\n"
                "• **How the Agent Detected It:** The memory scanner inspected rolling PRs for `CC-PU-BIW` and identified two separate 8-box requests for `TML-BIW-404` at ₹13,800/box. "
                "Individually, each order is ₹1,10,400 (< ₹2 Lakh), which would have slipped through auto-approval.\n\n"
                "• **The Merge & Governance Fix:** The agent merged both requisitions into a single order of **16 boxes** totaling **₹2,20,800**. "
                "This breached the ₹2 Lakh ceiling and was properly escalated to **Tier 2 (BIW Shop Head)**. Additionally, merging 8+8 satisfied supplier ITW India's MOQ of 10 boxes!"
            )

        # 5. Questions about Alternators / Volume Discount / Ariba Bundling / Savings
        if any(w in msg for w in ["alternator", "volume", "discount", "ariba", "707", "nexon", "punch", "altroz", "saving"]):
            return (
                "**Cross-Shop Volume Aggregation & Enterprise Savings:**\n\n"
                "• **The Multi-Line Demand:** Three vehicle platforms submitted independent demands for `TML-ELE-707` (12V 120A Alternators):\n"
                "  - Nexon Line: 800 units\n"
                "  - Punch Line: 600 units\n"
                "  - Altroz Line: 600 units\n\n"
                "• **Automated Bundling:** Rather than issuing three isolated purchase orders at the spot rate of ₹4,200, the agent consolidated the requisition into a **2,000-unit Master PO**.\n\n"
                "• **Ariba Enterprise Discount:** Crossing the 1,500-unit contract threshold triggered a **5% enterprise discount**:\n"
                "  - Discounted Unit Price: $₹4,200 \\times (1 - 0.05) = \\mathbf{₹3,990}$\n"
                "  - Gross Baseline: $2,000 \\times ₹4,200 = ₹84,00,000$\n"
                "  - Discounted Master PO: $2,000 \\times ₹3,990 = \\mathbf{₹79,80,000}$\n"
                "  - **Direct Bottom-Line Savings: ₹4,20,000**\n\n"
                "• **Routing:** Since ₹79,80,000 exceeds ₹15 Lakh, it is routed to **Tier 3 (Pune Plant Financial Controller)** for centralized multi-line release."
            )

        # 6. Questions about Budgets / Cost Centers
        if any(w in msg for w in ["budget", "cost center", "limit", "tier", "remaining"]):
            tcf = self.db.get_cost_center("CC-PU-TCF")
            biw = self.db.get_cost_center("CC-PU-BIW")
            pnt = self.db.get_cost_center("CC-PU-PAINT")
            return (
                "**Live Cost Center Financial Matrix & Balances:**\n\n"
                f"1. **CC-PU-TCF (Trim/Chassis/Final & EV):**\n"
                f"   • Remaining: **₹{tcf['remaining_budget']:,.2f}** / ₹{tcf['total_budget']:,.2f}\n"
                f"   • Approval Limits: Tier 1 (Auto) $\\le ₹4L$ | Tier 2 (Shop Head) $\\le ₹15L$ | Tier 3 (Finance) $> ₹15L$\n\n"
                f"2. **CC-PU-BIW (Body-in-White):**\n"
                f"   • Remaining: **₹{biw['remaining_budget']:,.2f}** / ₹{biw['total_budget']:,.2f}\n"
                f"   • Approval Limits: Tier 1 (Auto) $\\le ₹2L$ | Tier 2 (Shop Head) $\\le ₹6L$ | Tier 3 (Finance) $> ₹6L$\n\n"
                f"3. **CC-PU-PAINT (Paint Shop):**\n"
                f"   • Remaining: **₹{pnt['remaining_budget']:,.2f}** / ₹{pnt['total_budget']:,.2f}\n"
                f"   • Approval Limits: Tier 1 (Auto) $\\le ₹3L$ | Tier 2 (Shop Head) $\\le ₹10L$ | Tier 3 (Finance) $> ₹10L$\n\n"
                "If any purchase order exceeds the remaining balance, the Hard Budget Guardrail automatically halts the transaction and calculates the maximum affordable quantity."
            )

        # 7. Questions about Line Stoppage / JIT Cost
        if any(w in msg for w in ["stoppage", "downtime", "hour", "cost", "loss"]):
            return (
                "**JIT Assembly Line Economics at Pune Plant:**\n\n"
                "Tata Motors' assembly lines for high-volume platforms (Nexon, Punch, Harrier, Safari) run on synchronous Just-In-Time schedules. "
                "Any feeder stoppage halts downstream robotic cells and hundreds of line workers, causing financial losses of **₹15 Lakh to ₹22 Lakh per hour**.\n\n"
                "This Autonomous Procurement Agent eliminates manual buyer delays by evaluating alternate suppliers, verifying MOQ, checking quality thresholds, "
                "and calculating price premiums within milliseconds to dispatch POs directly into SAP Ariba."
            )

        # 8. Questions about the most recent transaction
        if last_po and any(w in msg for w in ["last", "latest", "recent", "po", "just now", "what did you do"]):
            vendor = last_po["vendor"]
            return (
                f"**Summary of Most Recent Transaction ({last_po['po_number']}):**\n\n"
                f"• **Material:** {last_po['line_items'][0]['material_code']} ({last_po['line_items'][0]['description']})\n"
                f"• **Quantity:** {last_po['line_items'][0]['quantity']} {last_po['line_items'][0]['unit']}\n"
                f"• **Supplier:** {vendor['id']} - {vendor['name']} ({vendor['location']})\n"
                f"• **Total Value:** ₹{last_po['total_value_inr']:,.2f}\n"
                f"• **Action Taken:** **{last_po['action']}** ({last_po['approval_routing']})\n"
                f"• **Guardrails Enforced:** {', '.join(last_po['guardrails']) if last_po['guardrails'] else 'Standard Sourcing'}\n"
                f"• **SAP ERP Status:** `{last_po['erp_status']}`"
            )

        # General / fallback response
        return (
            "**Tata Motors Pune Procurement Copilot at your service.**\n\n"
            "I can explain every autonomous decision, financial calculation, and compliance check performed by our engine. You can ask me:\n"
            "• *'Why was Shenzhen Tech blocked for EV battery paste?'*\n"
            "• *'How did you calculate the JIT premium for Uno Minda?'*\n"
            "• *'Explain the anti-split rule on weld electrode caps.'*\n"
            "• *'Why was Kansai Nerolac put on Quality Hold?'*\n"
            "• *'How did volume aggregation save ₹4.20 Lakh on alternators?'*\n"
            "• *'What are the current budget limits and remaining balances?'*"
        )


chatbot = ProcurementChatbot()
