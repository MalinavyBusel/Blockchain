from uuid import uuid4

from flask import Flask, jsonify, request

from blockchain_implementation import Blockchain


app = Flask(__name__)
node_identifier = str(uuid4()).replace("-", "")
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(
        sender=0,
        recipient=node_identifier,
        amount=1,
    )

    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "Forged new block.",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"]
    }
    return jsonify(response), 200


@app.route("/transaction/new", methods=["POST"])
def transaction_new():
    values = request.get_json(True)
    required = ["sender", "recipient", "amount"]

    if not all(k in values for k in required):
        return "Missing values", 400

    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {"message": f"Transaction will be added to the Block {index}."}

    return jsonify(response, 200)


@app.route("/chain", methods=["GET"])
def chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route("/nodes/register", methods = ["POST"])
def register_new_miner():
    values = request.get_json(True)

    nodes = values.get("nodes")
    if not nodes:
        return "Error: Please supply list of valid nodes", 400

    for node in nodes:
        blockchain.register_miner_node(node)

    response = {
        'message': 'New nodes have been added.',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 200


@app.route("/miner/nodes/resolve", methods = ["GET"])
def consensus():
    conflicts = blockchain.resolve_conflicts()

    if conflicts:
        response = {
            'message': 'Our chain was replaced.',
            'new_chain': blockchain.chain,
        }
        return jsonify(response), 200

    response = {
        'message': 'Our chain is authoritative.',
        'chain': blockchain.chain,
    }
    return jsonify(response), 200


if __name__ == "__main__":
    app.run("0.0.0.0", 5001)
