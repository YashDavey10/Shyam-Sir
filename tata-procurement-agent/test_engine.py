import sys
import io

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from erp_data import erp_db
from engine import engine


def run_tests():
    print("=================================================================")
    print("STARTING TEST SUITE: TATA MOTORS AUTONOMOUS PROCUREMENT AGENT")
    print("=================================================================\n")

    # Reset ERP database before testing
    erp_db.reset()

    # -------------------------------------------------------------
    # Scenario 1: JIT Pivot
    # "Short 400 ABS sensors (TML-PV-101) for TCF line. Need in 24 hrs."
    # -------------------------------------------------------------
    print("--- [TEST 1] Scenario 1: JIT Emergency Routing ---")
    s1_text = "Short 400 ABS sensors (TML-PV-101) for TCF line. Need in 24 hrs."
    json1, telemetry1, po1 = engine.process_pr(s1_text)
    
    print(f"Action: {json1['Action']}")
    print(f"Supplier: {json1['Selected_Supplier']}")
    print(f"Calculations: {json1['Calculations']}")
    print(f"Guardrails: {json1['Guardrails_Triggered']}")
    print(f"Reasoning: {json1['Reasoning']}\n")

    assert json1["Material_Code"] == "TML-PV-101", f"Expected TML-PV-101, got {json1['Material_Code']}"
    assert "SUP-02" in json1["Selected_Supplier"], f"Expected Uno Minda (SUP-02), got {json1['Selected_Supplier']}"
    assert json1["Calculations"]["Requested_Qty"] == 400
    assert json1["Calculations"]["Final_Unit_Rate_INR"] == 625.0
    assert abs(json1["Calculations"]["Premium_or_Discount_Applied_Pct"] - 7.76) < 0.1
    assert json1["Calculations"]["Total_PO_Value_INR"] == 250000.0
    assert json1["Action"] == "AUTO-APPROVED"
    assert "JIT Pivot" in json1["Guardrails_Triggered"]
    print(">>> TEST 1 PASSED!\n")

    # -------------------------------------------------------------
    # Scenario 2: PLI Block
    # "Order 20 pails of EV paste (TML-EV-303) from Shenzhen Tech at ₹29,000 to save money."
    # -------------------------------------------------------------
    print("--- [TEST 2] Scenario 2: Regulatory PLI Hard Block ---")
    s2_text = "Order 20 pails of EV paste (TML-EV-303) from Shenzhen Tech at ₹29,000 to save money."
    json2, telemetry2, po2 = engine.process_pr(s2_text)

    print(f"Action: {json2['Action']}")
    print(f"Supplier: {json2['Selected_Supplier']}")
    print(f"Calculations: {json2['Calculations']}")
    print(f"Guardrails: {json2['Guardrails_Triggered']}")
    print(f"Reasoning: {json2['Reasoning']}\n")

    assert json2["Material_Code"] == "TML-EV-303"
    assert "SUP-05" in json2["Selected_Supplier"], f"Expected Henkel India (SUP-05), got {json2['Selected_Supplier']}"
    assert json2["Calculations"]["Requested_Qty"] == 20
    assert json2["Calculations"]["Final_Unit_Rate_INR"] == 36500.0
    assert json2["Calculations"]["Total_PO_Value_INR"] == 730000.0
    assert json2["Action"] == "ESCALATED TO TIER 2"
    assert "PLI Block" in json2["Guardrails_Triggered"]
    print(">>> TEST 2 PASSED!\n")

    # -------------------------------------------------------------
    # Scenario 3: Quality Gate
    # "Need 10 drums of CED primer (TML-PNT-505) from Kansai Nerolac."
    # -------------------------------------------------------------
    print("--- [TEST 3] Scenario 3: IATF-16949 Quality Gate ---")
    s3_text = "Need 10 drums of CED primer (TML-PNT-505) from Kansai Nerolac."
    json3, telemetry3, po3 = engine.process_pr(s3_text)

    print(f"Action: {json3['Action']}")
    print(f"Supplier: {json3['Selected_Supplier']}")
    print(f"Calculations: {json3['Calculations']}")
    print(f"Guardrails: {json3['Guardrails_Triggered']}")
    print(f"Reasoning: {json3['Reasoning']}\n")

    assert json3["Material_Code"] == "TML-PNT-505"
    assert "SUP-10" in json3["Selected_Supplier"], f"Expected PPG Asian Paints (SUP-10), got {json3['Selected_Supplier']}"
    assert json3["Calculations"]["Requested_Qty"] == 10
    assert json3["Calculations"]["Final_Unit_Rate_INR"] == 82500.0
    assert json3["Calculations"]["Total_PO_Value_INR"] == 825000.0
    assert json3["Action"] == "ESCALATED TO TIER 2"
    assert "Quality Hold" in json3["Guardrails_Triggered"]
    print(">>> TEST 3 PASSED!\n")

    # -------------------------------------------------------------
    # Scenario 4: Anti-Split Rule
    # Two requests from CC-PU-BIW for 8 boxes of weld caps (TML-BIW-404) at ₹13,800
    # -------------------------------------------------------------
    print("--- [TEST 4] Scenario 4: Anti-Split Heuristic Enforcement ---")
    s4_text_part1 = "Request 8 boxes of weld caps (TML-BIW-404) for CC-PU-BIW."
    json4_1, _, _ = engine.process_pr(s4_text_part1)
    
    # Second PR within 48h for same material in BIW
    s4_text_part2 = "Second request: 8 boxes of weld caps (TML-BIW-404) for CC-PU-BIW."
    json4_2, telemetry4, po4 = engine.process_pr(s4_text_part2)

    print(f"Action: {json4_2['Action']}")
    print(f"Supplier: {json4_2['Selected_Supplier']}")
    print(f"Calculations: {json4_2['Calculations']}")
    print(f"Guardrails: {json4_2['Guardrails_Triggered']}")
    print(f"Reasoning: {json4_2['Reasoning']}\n")

    assert json4_2["Material_Code"] == "TML-BIW-404"
    assert "SUP-07" in json4_2["Selected_Supplier"]
    assert json4_2["Calculations"]["Requested_Qty"] == 16, f"Expected 16 boxes, got {json4_2['Calculations']['Requested_Qty']}"
    assert json4_2["Calculations"]["Final_Unit_Rate_INR"] == 13800.0
    assert json4_2["Calculations"]["Total_PO_Value_INR"] == 220800.0
    assert json4_2["Action"] == "ESCALATED TO TIER 2", f"Expected ESCALATED TO TIER 2, got {json4_2['Action']}"
    assert "Anti-Split Rule" in json4_2["Guardrails_Triggered"]
    print(">>> TEST 4 PASSED!\n")

    # -------------------------------------------------------------
    # Scenario 5: Volume Aggregation
    # Nexon needs 800 Alternators, Punch needs 600, Altroz needs 600 (TML-ELE-707 at ₹4,200)
    # -------------------------------------------------------------
    print("--- [TEST 5] Scenario 5: Cross-Shop Volume Aggregation ---")
    s5_text = "Nexon needs 800 Alternators, Punch needs 600, Altroz needs 600 (TML-ELE-707 at ₹4,200)."
    json5, telemetry5, po5 = engine.process_pr(s5_text)

    print(f"Action: {json5['Action']}")
    print(f"Supplier: {json5['Selected_Supplier']}")
    print(f"Calculations: {json5['Calculations']}")
    print(f"Guardrails: {json5['Guardrails_Triggered']}")
    print(f"Reasoning: {json5['Reasoning']}\n")

    assert json5["Material_Code"] == "TML-ELE-707"
    assert json5["Calculations"]["Requested_Qty"] == 2000, f"Expected 2000 units, got {json5['Calculations']['Requested_Qty']}"
    assert json5["Calculations"]["Final_Unit_Rate_INR"] == 3990.0, f"Expected 3990.0, got {json5['Calculations']['Final_Unit_Rate_INR']}"
    assert json5["Calculations"]["Total_PO_Value_INR"] == 7980000.0, f"Expected 7980000.0, got {json5['Calculations']['Total_PO_Value_INR']}"
    assert json5["Action"] == "ESCALATED TO TIER 3", f"Expected ESCALATED TO TIER 3, got {json5['Action']}"
    assert any("Volume" in g for g in json5["Guardrails_Triggered"])
    print(">>> TEST 5 PASSED!\n")

    assert len(erp_db.email_outbox) > 0, "Expected email outbox to have recorded dispatched emails"
    print(f"Dispatched Supplier Emails in Outbox: {len(erp_db.email_outbox)}")
    first_email = erp_db.email_outbox[0]
    print(f"Latest Email Recipient: {first_email['recipient_email']}")
    print(f"Latest Email Subject: {first_email['subject']}")

    print("=================================================================")
    print("ALL 5 SYSTEM SCENARIOS & EMAIL DISPATCH VALIDATED!")
    print("=================================================================")


if __name__ == "__main__":
    run_tests()
