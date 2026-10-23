# -*- coding: utf-8 -*-
"""MCP Server for FMC OSRA-22 Ocean Freight Demurrage Dispute Arbiter Skill."""
import sys
import json
import logging
from typing import Dict, Any

from client import FMCOSRA22DemurrageDisputeArbiter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TOOLS_SCHEMA = [
    {
        "name": "audit_demurrage_invoice_osra_compliance",
        "description": "Verify carrier invoice against 13 mandatory OSRA-22 statutory billing data elements.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "invoice_metadata": {
                    "type": "object",
                    "properties": {
                        "has_container_num": {
                            "type": "boolean"
                        },
                        "has_port_discharge_date": {
                            "type": "boolean"
                        },
                        "has_free_time_start_end": {
                            "type": "boolean"
                        },
                        "has_cert_allowed_empty_return": {
                            "type": "boolean"
                        },
                        "has_carrier_fmc_num": {
                            "type": "boolean"
                        }
                    }
                },
                "billed_demurrage_usd": {
                    "type": "number"
                }
            },
            "required": [
                "invoice_metadata",
                "billed_demurrage_usd"
            ]
        }
    },
    {
        "name": "generate_fmc_charge_complaint_packet",
        "description": "Generate formal FMC 46 U.S.C. \u00a7 41104(a) charge dispute complaint packet for immediate carrier fee cancellation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "carrier_name": {
                    "type": "string"
                },
                "bol_number": {
                    "type": "string"
                },
                "missing_elements": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    }
                },
                "disputed_amount_usd": {
                    "type": "number"
                }
            },
            "required": [
                "carrier_name",
                "bol_number",
                "disputed_amount_usd"
            ]
        }
    }
]

def handle_rpc(line: str) -> str:
    try:
        req = json.loads(line)
        method = req.get("method")
        msg_id = req.get("id")

        if method == "initialize":
            res = {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-freight-demurrage-osra22-dispute-arbiter-skill", "version": "1.0.0"}
            }
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": res})

        elif method == "tools/list":
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS_SCHEMA}})

        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name")
            args = params.get("arguments", {})

            target_func = getattr(FMCOSRA22DemurrageDisputeArbiter, tool_name, None)
            if not target_func:
                return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {tool_name}"}})

            result = target_func(**args)
            return json.dumps({
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            })

        else:
            return json.dumps({"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"Method not found: {method}"}})

    except Exception as e:
        return json.dumps({"jsonrpc": "2.0", "id": req.get("id") if "req" in locals() else None, "error": {"code": -32000, "message": str(e)}})

def run_test():
    init_req = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    init_res = json.loads(handle_rpc(init_req))
    assert init_res.get("result", {}).get("serverInfo", {}).get("name") == "genpark-agentic-commerce-freight-demurrage-osra22-dispute-arbiter-skill"

    list_req = json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    list_res = json.loads(handle_rpc(list_req))
    assert len(list_res.get("result", {}).get("tools", [])) == 2
    return True

if __name__ == "__main__":
    if "--test" in sys.argv:
        if run_test():
            sys.exit(0)
        sys.exit(1)

    for line in sys.stdin:
        if not line.strip():
            continue
        out = handle_rpc(line)
        sys.stdout.write(out + "\n")
        sys.stdout.flush()
