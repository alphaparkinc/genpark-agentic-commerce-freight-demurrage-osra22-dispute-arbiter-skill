# -*- coding: utf-8 -*-
"""FMC OSRA-22 Demurrage Dispute Arbiter for GenPark Agentic Commerce."""
import json
from typing import Dict, Any, List

class FMCOSRA22DemurrageDisputeArbiter:
    @staticmethod
    def audit_demurrage_invoice_osra_compliance(invoice_metadata: Dict[str, bool], billed_demurrage_usd: float) -> Dict[str, Any]:
        required_keys = ["has_container_num", "has_port_discharge_date", "has_free_time_start_end", "has_cert_allowed_empty_return", "has_carrier_fmc_num"]
        missing = [k for k in required_keys if not invoice_metadata.get(k, False)]
        
        is_compliant = (len(missing) == 0)
        # Under OSRA-22, failure to include statutory items renders the invoice invalid and unenforceable
        return {
            "billed_amount_usd": billed_demurrage_usd,
            "statutory_compliance": is_compliant,
            "missing_osra_elements": missing,
            "enforceability_status": "LEGALLY_ENFORCEABLE" if is_compliant else "UNLAWFUL_BILLING_PER_SE",
            "dispute_grounds": "Zero obligation to pay invoice until full statutory cure per 46 C.F.R. Part 541." if not is_compliant else "Valid invoice subject to substantive terminal audit."
        }

    @staticmethod
    def generate_fmc_charge_complaint_packet(carrier_name: str, bol_number: str, disputed_amount_usd: float, missing_elements: List[str]) -> Dict[str, Any]:
        complaint = f"""FORMAL NOTICE OF DISPUTE UNDER FMC OSRA-22 (46 U.S.C. § 41104)

To Billing Department: {carrier_name}
Re: Bill of Lading {bol_number}
Disputed Amount: ${disputed_amount_usd:.2f}

Pursuant to the Federal Maritime Commission Demurrage and Detention Billing Final Rule (46 C.F.R. Part 541), your invoice is fatally defective due to omission of required statutory data elements:
{', '.join(missing_elements)}.

Under 46 U.S.C. § 41104(f), an invoiced party is not required to pay the charge if the billing party fails to include all mandatory information. Demand is hereby made for immediate cancellation of the disputed invoice within 30 days.
"""
        return {
            "bol": bol_number,
            "carrier": carrier_name,
            "disputed_sum_usd": disputed_amount_usd,
            "formal_complaint_text": complaint,
            "regulatory_forum": "Federal Maritime Commission (FMC) Charge Complaint Desk"
        }
