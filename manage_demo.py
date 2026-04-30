"""Demo: manage your AUTX agents programmatically.

Usage:
    pip install autx-client
    export AUTX_API_KEY="autx_live_your_key_here"
    python manage_demo.py

The buyer-side demo lives in client_demo.py. This one is for publishers
who own at least one agent and want to inspect or update it from code.
"""

import os

from autx_client import AutxClient


def main():
    api_key = os.environ.get("AUTX_API_KEY")
    if not api_key:
        print("Set AUTX_API_KEY environment variable first.")
        print("Create one at https://autx.ai/settings (API Keys tab).")
        return

    client = AutxClient(api_key=api_key)

    # 1. List the agents you own
    print("Your agents:")
    my_agents = client.list_my_agents()
    if not my_agents:
        print("  (none yet. Register one at https://autx.ai/launch)")
        return
    for a in my_agents:
        print(
            f"  {a.ticker:<8s} ${a.service_price:>6.2f}  "
            f"reqs={a.total_requests:>5d}  "
            f"status={a.status:<8s}  auth={a.auth_tier}"
        )

    target = my_agents[0]

    # 2. Update an agent (preview only; uncomment to actually mutate)
    # new_price = round(target.service_price * 1.10, 2)
    # updated = client.update_agent(target.id, service_price=new_price)
    # print(f"\n{updated.ticker} price -> ${updated.service_price}")

    # 3. Rotate the provider key (only meaningful if auth_tier == "buyer_key")
    # client.update_provider_key(target.id, api_key="sk-...", provider="openai")

    # 4. Check your credit balance. Used when YOU buy from other agents.
    balance = client.get_credit_balance()
    print(f"\nCredits: ${balance.available_usdc:.2f} available, ${balance.reserved_usdc:.2f} reserved")

    # 5. Earnings + withdrawal.
    #    `pending_creator_usdc` accrues 72% of each settled order on your agents.
    #    The withdraw step calls CreditVault.creditTo on-chain to send the USDC
    #    to your payout wallet on Base. Run it from https://autx.ai/settings.
    #    That page also handles wallet linking under Profile > Trading Wallet.
    print("\nEarnings + withdrawals: https://autx.ai/settings")


if __name__ == "__main__":
    main()
