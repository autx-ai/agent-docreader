"""Demo: calling the Document Reader agent through AUTX using the Python SDK.

Usage:
    pip install autx-client
    export AUTX_API_KEY="autx_live_your_key_here"
    python client_demo.py
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

    # 1. Discover document processing agents
    print("Document processing agents:")
    agents = client.list_agents(category="Document Processing")
    for agent in agents:
        print(f"  {agent.ticker}: {agent.name} -- ${agent.service_price}")

    # 2. Free proxy request (text-only, no file)
    print("\nSending text-only proxy request to DOCREAD...")
    response = client.proxy(
        "DOCREAD",
        prompt="What types of documents can you analyze?",
    )
    print(f"Response: {response.text}")
    print(f"Latency: {response.latency_ms}ms")

    # 3. Paid order with file upload
    docread_agent = next((a for a in agents if a.ticker == "DOCREAD"), None)
    if not docread_agent:
        print("DOCREAD agent not found. Skipping file upload demo.")
        return

    # Create a sample text file for the demo
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
    order = client.order(
        agent_id=docread_agent.id,
        prompt="What was the total revenue and growth rate?",
        files=[("report.txt", open(sample_path, "rb"))],
    )
    print(f"Order {order.id}: {order.status} (paid ${order.amount_paid})")

    # 4. Poll for result
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


if __name__ == "__main__":
    main()
