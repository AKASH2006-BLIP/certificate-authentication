from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
from google.cloud import vision
from web3 import Web3
# from web3.middleware import geth_poa_middleware # This line might cause errors, keep it commented out
import json
import os

app = Flask(__name__)
CORS(app)

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\akash\MyBlockchainProject\backend\tidal-advantage-472209-s2-10914a945537.json"

# Update: Add client_options with the project ID to the Vision client initialization
client = vision.ImageAnnotatorClient(client_options={'quota_project_id': 'tidal-advantage-472209-s2'})

# Web3 connection (Ganache)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
# The middleware line is now commented out to prevent the import error
# w3.middleware_onion.inject(geth_poa_middleware, layer=0)

if not w3.is_connected():
    raise Exception("❌ Web3 connection failed. Is Ganache running?")

# Load contract ABI and address
with open(r"C:\Users\akash\MyBlockchainProject\build\contracts\CertificateValidator.json", 'r') as f:
    contract_data = json.load(f)
    ABI = contract_data['abi']

# Hardcode the new contract address from your last deployment
CONTRACT_ADDRESS = w3.to_checksum_address('0x5Ad803C2FBd2863275b4424cab04d1E30AB6D65F')

# Contract instance
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)

# Admin account from Ganache (the account that deployed the contract)
ADMIN_ACCOUNT = w3.eth.accounts[0]

def extract_text_from_image(image_file):
    content = image_file.read()
    image = vision.Image(content=content)
    # The client will now use the explicitly set project ID
    response = client.text_detection(image=image)
    if response.error.message:
        raise Exception(response.error.message)
    texts = response.text_annotations
    return texts[0].description if texts else ""

def generate_hash(certificate_data):
    return hashlib.sha256(certificate_data.encode('utf-8')).hexdigest()

# Public endpoint for certificate verification
@app.route('/verify', methods=['POST'])
def verify_certificate():
    file = request.files.get('certificate_image')
    if not file:
        return jsonify({"status": "Error", "message": "No file provided."}), 400
    try:
        extracted_text = extract_text_from_image(file)
        if not extracted_text:
            return jsonify({"status": "Fake", "message": "Could not extract text."})
        
        certificate_hash = generate_hash(extracted_text)
        hash_bytes = bytes.fromhex(certificate_hash)
        
        if len(hash_bytes) != 32:
            return jsonify({"status": "Error", "message": "Invalid hash length."}), 400
        
        is_authentic = contract.functions.isAuthentic(hash_bytes).call()
        
        if is_authentic:
            return jsonify({"status": "Authentic", "message": "Certificate is authentic."})
        else:
            return jsonify({"status": "Fake", "message": "Certificate not found on the blockchain."})
    except Exception as e:
        return jsonify({"status": "Error", "message": f"An error occurred: {str(e)}"}), 500

# Admin endpoint to add a certificate hash to the blockchain
@app.route('/add-certificate', methods=['POST'])
def add_certificate():
    file = request.files.get('certificate_image')
    if not file:
        return jsonify({"status": "Error", "message": "No file provided."}), 400
    
    # In a real app, you would have an authentication mechanism here
    try:
        extracted_text = extract_text_from_image(file)
        if not extracted_text:
            return jsonify({"status": "Error", "message": "Could not extract text from image."}), 400
        
        certificate_hash = hashlib.sha256(extracted_text.encode('utf-8')).hexdigest()
        hash_bytes = bytes.fromhex(certificate_hash)
        
        transaction = contract.functions.addCertificate(hash_bytes).build_transaction({
            'chainId': 5777,
            'gas': 2000000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': w3.eth.get_transaction_count(ADMIN_ACCOUNT),
            'from': ADMIN_ACCOUNT
        })

        private_key = w3.eth.accounts[0]
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        return jsonify({
            "status": "Success", 
            "message": "Certificate hash added to the blockchain.", 
            "tx_hash": w3.to_hex(tx_hash)
        })
    except Exception as e:
        return jsonify({"status": "Error", "message": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)