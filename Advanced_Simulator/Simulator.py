import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import hashlib
import json
from time import time, sleep
from uuid import uuid4
from threading import Thread
import socket
import pickle
import random

# ------------------------ Block Definition ------------------------ #

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

# ------------------------ Blockchain Definition ------------------------ #

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()
        self.nodes = set()
        self.current_transactions = []

    def create_genesis_block(self):
        genesis_block = Block(0, [], time(), "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return block_hash.startswith('0000') and block_hash == block.compute_hash()

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0000'):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def add_new_transaction(self, transaction):
        self.current_transactions.append(transaction)

    @property
    def last_block(self):
        return self.chain[-1]

# ------------------------ Smart Contract ------------------------ #

class SmartContract:
    def __init__(self, buyer, seller, amount):
        self.buyer = buyer
        self.seller = seller
        self.amount = amount
        self.released = False
        self.disputed = False
        self.id = str(uuid4())

    def confirm_delivery(self):
        if not self.disputed:
            self.released = True
            return {"result": f"Funds ({self.amount}) released to {self.seller}.", "contract": self}

    def raise_dispute(self):
        self.disputed = True
        return {"result": f"Dispute raised. Funds ({self.amount}) held.", "contract": self}

    def refund_buyer(self):
        if self.disputed and not self.released:
            return {"result": f"Funds ({self.amount}) refunded to {self.buyer}.", "contract": self}

# ------------------------ Blockchain Visualizer ------------------------ #

class BlockchainVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.G = nx.DiGraph()
        self.pos = {}

    def update_graph(self, blockchain):
        self.G.clear()
        self.pos = {}

        for i, block in enumerate(blockchain.chain):
            block_label = f"Block {block.index}\nHash: {block.hash[:8]}...\nPrev: {block.previous_hash[:8]}..."
            self.G.add_node(block_label)
            self.pos[block_label] = (i, 0)

            if i > 0:
                prev_label = f"Block {blockchain.chain[i-1].index}\nHash: {blockchain.chain[i-1].hash[:8]}...\nPrev: {blockchain.chain[i-1].previous_hash[:8]}..."
                self.G.add_edge(prev_label, block_label)

        plt.clf()
        nx.draw(self.G, self.pos, with_labels=True, node_size=3000, node_color='skyblue',
                font_size=8, arrows=True, ax=self.ax)
        plt.title("Blockchain Structure", fontsize=15)
        plt.draw()
        plt.pause(0.1)

# ------------------------ Node Class ------------------------ #

class Node:
    def __init__(self, port):
        self.blockchain = Blockchain()
        self.port = port
        self.peers = []
        self.contracts = {}
        self.visualizer = BlockchainVisualizer() if port == 6000 else None  # Only main node visualizes

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('localhost', self.port))
        server.listen(5)
        while True:
            client, addr = server.accept()
            Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        data = client.recv(4096)
        if not data:
            return
        message = pickle.loads(data)
        if message['type'] == 'transaction':
            self.handle_transaction(message['data'])
        elif message['type'] == 'block':
            self.handle_block(message['data'])
        elif message['type'] == 'contract':
            self.handle_contract(message['data'])
        client.close()

    def handle_transaction(self, transaction):
        self.blockchain.add_new_transaction(transaction)
        if len(self.blockchain.current_transactions) >= 2:
            self.mine_block()

    def handle_block(self, block_data):
        block = block_data['block']
        hash_ = block_data['hash']
        if self.blockchain.add_block(block, hash_):
            print(f"Node {self.port}: New block added")
            if self.visualizer:
                self.visualizer.update_graph(self.blockchain)
        else:
            print(f"Node {self.port}: Invalid block rejected")

    def handle_contract(self, contract_data):
        action = contract_data['action']
        contract_id = contract_data['contract_id']
        if contract_id not in self.contracts:
            self.contracts[contract_id] = contract_data['contract']
        contract = self.contracts[contract_id]
        if action == 'confirm':
            result = contract.confirm_delivery()
        elif action == 'dispute':
            result = contract.raise_dispute()
        elif action == 'refund':
            result = contract.refund_buyer()
        self.broadcast_contract(result['contract'])

    def mine_block(self):
        last_block = self.blockchain.last_block
        new_block = Block(
            index=last_block.index + 1,
            transactions=self.blockchain.current_transactions,
            timestamp=time(),
            previous_hash=last_block.hash
        )
        proof = self.blockchain.proof_of_work(new_block)
        self.blockchain.add_block(new_block, proof)

        if self.visualizer:
            self.visualizer.update_graph(self.blockchain)

        self.broadcast_block(new_block, proof)
        self.blockchain.current_transactions = []

    def broadcast_block(self, block, proof):
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', peer))
                s.send(pickle.dumps({'type': 'block', 'data': {'block': block, 'hash': proof}}))
                s.close()
            except:
                continue

    def broadcast_contract(self, contract):
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', peer))
                s.send(pickle.dumps({
                    'type': 'contract',
                    'data': {
                        'action': action,  # must be passed in function
                        'contract_id': contract.id,
                        'contract': contract
                    }
                }))
                s.close()
            except:
                continue

    def connect_to_peer(self, port):
        if port != self.port and port not in self.peers:
            self.peers.append(port)

    def send_transaction(self, transaction):
        for peer in self.peers:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(('localhost', peer))
                s.send(pickle.dumps({'type': 'transaction', 'data': transaction}))
                s.close()
            except:
                continue

# ------------------------ Simulation ------------------------ #

def simulate_network():
    ports = [6000, 6001, 6002, 6003]
    nodes = [Node(port) for port in ports]

    plt.ion()  # Turn on interactive plotting

    for i, node in enumerate(nodes):
        for port in ports[:i] + ports[i+1:]:
            node.connect_to_peer(port)
        Thread(target=node.start_server).start()

    main_node = nodes[0]

    contract = SmartContract("Alice", "Bob", 100)
    main_node.contracts[contract.id] = contract
    for node in nodes[1:]:
        node.contracts[contract.id] = contract

    print("Initializing escrow contract...")
    if main_node.visualizer:
        main_node.visualizer.update_graph(main_node.blockchain)

    print("\nSimulating normal transaction flow:")
    main_node.send_transaction({"from": "Alice", "to": "Escrow", "amount": 100})
    sleep(2)

    print("\nSeller delivers product, buyer confirms:")
    result = contract.confirm_delivery()
    main_node.broadcast_contract(result['contract'])
    sleep(1)

    print("\nSimulating dispute scenario:")
    contract2 = SmartContract("Charlie", "Dave", 50)
    main_node.contracts[contract2.id] = contract2
    for node in nodes[1:]:
        node.contracts[contract2.id] = contract2

    main_node.send_transaction({"from": "Charlie", "to": "Escrow", "amount": 50})
    sleep(2)

    print("\nBuyer raises dispute:")
    result = contract2.raise_dispute()
    main_node.broadcast_contract(result['contract'])
    sleep(1)

    print("\nProcessing refund:")
    result = contract2.refund_buyer()
    main_node.broadcast_contract(result['contract'])

    plt.ioff()
    plt.show()

if __name__ == "__main__":
    simulate_network()
