import zmq
import json
import os

SAVE_DIR = "saved_data"
SAVE_FILE = os.path.join(SAVE_DIR, "playersdata.dat")
ENCRYPTION_KEY = 23

os.makedirs(SAVE_DIR, exist_ok=True)

def encrypt_data(data: str, key: int = ENCRYPTION_KEY) -> bytes:
    return bytes([b ^ key for b in data.encode('utf-8')])

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Microservice A (Save Service) running...")

while True:
    try:
        # Load data
        message = socket.recv_json()
        print("Received:", message)

        # Validate required keys
        if not all(k in message for k in ["playerPosition", "ButtonTriggered"]):
            raise ValueError("Invalid data format. Missing required keys.")

        # Encrypt and save
        encrypted_data = encrypt_data(json.dumps(message))
        with open(SAVE_FILE, "wb") as f:
            f.write(encrypted_data)

        socket.send_json({"status": "success", "message": "Player data saved."})

    except Exception as e:
        print("Error:", e)
        socket.send_json({"error": str(e)})
        socket.close()
        context.term()
