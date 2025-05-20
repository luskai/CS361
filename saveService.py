import zmq
import json
import os

SAVE_DIR = "saved_data"
SAVE_FILE = os.path.join(SAVE_DIR, "playersdata.dat")
ENCRYPTION_KEY = 23

os.makedirs(SAVE_DIR, exist_ok=True)

def encrypt_data(data: str, key: int = ENCRYPTION_KEY) -> bytes:
    return bytes([b ^ key for b in data.encode('utf-8')])

def decrypt_data(data: bytes, key: int = ENCRYPTION_KEY) -> str:
    return ''.join([chr(b ^ key) for b in data])

def load_existing_data() -> dict:
    if not os.path.exists(SAVE_FILE):
        return {"playerData": []}
    with open(SAVE_FILE, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = decrypt_data(encrypted)
        return json.loads(decrypted)
    except Exception as e:
        print("Failed to decrypt/load existing data:", e)
        return {"playerData": []}

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Microservice A (Save Service) running...")

while True:
    try:
        message = socket.recv_json()
        print("Received:", message)

        # Load existing data
        data_store = load_existing_data()
        current_data = data_store["playerData"] # load player data list

        for new_entry in message["playerData"]:
            new_id = new_entry[0]
            updated = False
            for i, existing_entry in enumerate(current_data):
                if existing_entry[0] == new_id:
                    current_data[i] = new_entry
                    updated = True
                    break
            if not updated:
                current_data.append(new_entry)

        # Save data and encrypt
        updated_data = {"playerData": current_data}
        encrypted_data = encrypt_data(json.dumps(updated_data))
        with open(SAVE_FILE, "wb") as f:
            f.write(encrypted_data)

        socket.send_json({"status": "success", "message": "Player data saved."})


    except Exception as e:
        print("Error:", e)
        socket.send_json({"error" : str(e)})
