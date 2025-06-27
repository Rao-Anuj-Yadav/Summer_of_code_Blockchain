# in this python file i have tried to write a very basic python script 
#  that enforces predefined conditions and executes actions automatically. 
# While this won't be as secure or decentralized as a real blockchain-based smart contract,
#  this helped me in illustrate the core concept.


class EscrowSmartContract:
    def __init__(self, buyer, seller, amount):
        self.buyer = buyer
        self.seller = seller
        self.amount = amount
        self.released = False
        self.disputed = False

    def confirm_delivery(self):
        if not self.disputed:
            self.released = True
            return f"💰 Funds ({self.amount}) released to {self.seller}."
        else:
            return "❌ Dispute active. Funds cannot be released."

    def raise_dispute(self):
        self.disputed = True
        return f"⚖️ Dispute raised. Funds ({self.amount}) held for resolution."

    def refund_buyer(self):
        if self.disputed and not self.released:
            return f"🔙 Funds ({self.amount}) refunded to {self.buyer}."
        else:
            return "❌ No refund possible."


if __name__ == "__main__":
    
    escrow = EscrowSmartContract("Alice", "Bob", 100)

    print("1. Buyer sends funds to escrow.")
    print(f"   Escrow holds: {escrow.amount}")

    print("\n2. Seller delivers product. Buyer confirms.")
    print(escrow.confirm_delivery())  

    # Alternatively, if buyer disputes
    escrow_dispute = EscrowSmartContract("Alice", "Bob", 100)
    print("\n--- Alternate Scenario: Dispute ---")
    print("\n1. Buyer sends funds to escrow.")
    print(f"   Escrow holds: {escrow_dispute.amount}")

    print("\n2. Buyer raises a dispute.")
    print(escrow_dispute.raise_dispute())

    print("\n3. Escrow refunds buyer due to dispute.")
    print(escrow_dispute.refund_buyer())



# ran the terminal command  % python3 smart_contract_simulation.py >> output.txt 
