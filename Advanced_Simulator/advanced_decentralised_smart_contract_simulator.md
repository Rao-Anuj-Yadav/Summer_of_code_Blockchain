# 🧠 Blockchain + Escrow Smart Contract Simulation in Python

This notebook documents a simple implementation of a blockchain-based P2P network with **escrow-style smart contracts** using **Python**, **sockets**, and **multithreading**.

---

## 🧱 1. Block Class

**Purpose:**  
Defines the structure of a block in the blockchain.

**Attributes:**
- `index`: Position in the chain.
- `transactions`: List of transactions in the block.
- `timestamp`: Time of creation.
- `previous_hash`: Hash of the previous block.
- `nonce`: Used for Proof-of-Work (PoW).
- `hash`: SHA-256 hash of the current block.

**Key Method:**
- `compute_hash()`: Converts block data to a JSON string and hashes it with SHA-256.

---

## 🔗 2. Blockchain Class

**Purpose:**  
Manages the full blockchain — handles adding blocks, mining, and transaction management.

**Main Methods:**
- `create_genesis_block()`: Initializes the blockchain with a genesis block.
- `add_block(block, proof)`: Verifies proof and adds a block to the chain.
- `is_valid_proof(block, block_hash)`: Ensures hash starts with `'0000'` and matches computed hash.
- `proof_of_work(block)`: Increments nonce until valid hash is found.
- `add_new_transaction(transaction)`: Queues a new transaction for the next block.

**Property:**
- `last_block`: Returns the last block in the chain.

---

## 🤖 3. SmartContract Class

**Purpose:**  
Simulates an **escrow smart contract** for secure transactions between buyers and sellers.

**Attributes:**
- `buyer`, `seller`, `amount`: Parties involved in the contract.
- `released`: Whether funds are released.
- `disputed`: Whether a dispute has been raised.
- `id`: Unique ID (`UUID`).

**Key Methods:**
- `confirm_delivery()`: Marks delivery complete; releases funds to seller.
- `raise_dispute()`: Flags the contract as disputed.
- `refund_buyer()`: Returns funds to buyer if a dispute is unresolved.

---

## 🌐 4. Node Class

**Purpose:**  
Represents a blockchain node that can:
- Send/receive transactions and blocks
- Manage smart contracts
- Communicate over TCP using sockets

**Core Components:**
- `blockchain`: The local blockchain instance.
- `port`: Port number for this node.
- `peers`: List of other peer ports.
- `contracts`: Local smart contracts.

**Networking:**
- `start_server()`: Listens for incoming socket messages.
- `handle_client(client)`: Parses and dispatches messages.

**Handlers:**
- `handle_transaction(txn)`: Adds a transaction and mines a block if needed.
- `handle_block(data)`: Validates and adds a block.
- `handle_contract(data)`: Performs contract operations and broadcasts changes.

**Communication:**
- `broadcast_block(block, proof)`: Sends mined block to all peers.
- `broadcast_contract(contract)`: Shares updated contract.
- `connect_to_peer(port)`: Adds a peer node.
- `send_transaction(transaction)`: Sends transaction to all peers.

---

## 🚦 5. simulate_network() Function

**Purpose:**  
Simulates a 4-node blockchain network with two escrow contract flows.

### Steps:
1. Creates 4 nodes on ports `5000-5003`.
2. Connects each node to all others (full mesh).
3. Starts server threads for each node.
4. Initializes contract between:
   - Alice → Bob (100 units)
   - Charlie → Dave (50 units)

### Simulated Events:
- Alice sends payment to escrow.
- Alice confirms delivery; funds released to Bob.
- Charlie sends payment to escrow.
- Charlie raises dispute.
- Funds refunded to Charlie.

---

## 📦 Message Passing (Networking)

Each socket message is:
- Serialized using `pickle`.
- Structured as:  
  ```python
  {
    'type': 'transaction' | 'block' | 'contract',
    'data': payload_data
  }
