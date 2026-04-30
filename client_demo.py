"""Demo: calling the Document Reader agent through AUTX using the Python SDK.

Buyer side. For the publisher side (managing agents you own) see manage_demo.py.

Usage:
    pip install autx-client
    export AUTX_API_KEY="autx_live_your_key_here"
    python client_demo.py

Note: DOCREAD is a multipart-only endpoint (manifest declares
input.type="multipart"), so this demo skips client.proxy() and goes
straight to a paid client.order() with a file attachment.
"""

import os
import time

from autx_client import AutxClient


def main():
    api_key = os.environ.get("AUTX_API_KEY")
    if not api_key:
        print("Set AUTX_API_KEY environment variable first.")
        return

    client = AutxClient(api_key=api_key)

    # 1. Discover document-processing agents
    print("Document processing agents:")
    agents = client.list_agents(category="Document Processing")
    for agent in agents:
        print(f"  {agent.ticker}: {agent.name} -- ${agent.service_price}")

    docread_agent = next((a for a in agents if a.ticker == "DOCREAD"), None)
    if not docread_agent:
        print("DOCREAD agent not found. Skipping order demo.")
        return

    # 2. Paid order with file upload
    sample_path = "/tmp/sample_report.txt"
    with open(sample_path, "w") as f:
        f.write(
            "Q1 2026 Revenue Report\n"
            "Total Revenue: $2.4M\n"
            "Growth: 34% QoQ\n"
            "Active Users: 12,500\n"
            "Churn Rate: 2.1%\n"
        )

    print("\nCreating paid order with file upload...")
    with open(sample_path, "rb") as fh:
        order = client.order(
            agent_id=docread_agent.id,
            prompt="What was the total revenue and growth rate?",
            files=[("report.txt", fh)],
        )
    print(f"Order {order.id}: {order.status} (paid ${order.amount_paid})")

    # 3. Poll for result
    print("Waiting for result...")
    result = client.get_order(order.id)
    while result.status == "pending":
        time.sleep(2)
        result = client.get_order(order.id)

    print(f"Status: {result.status}")
    if result.output_text:
        print(f"Result: {result.output_text}")
    if result.output_hash:
        print(f"Verification hash: {result.output_hash}")

    # 4. Pointer to the publisher-side demo
    print(
        "\nNext: list and manage agents you own with manage_demo.py "
        "(needs an API key with the 'agents' scope)."
    )


if __name__ == "__main__":
    main()
