import zmq
import json

# Set up ZeroMQ
context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# Sample data in the correct format
player_data_payload = {
    "playerPosition": {
        "x": -3.974482536315918,
        "y": 0.9830012321472168,
        "z": -0.0180283784866333
    },
    "ButtonTriggered": [
        False, False, False, False, False
    ]
}


# Send the JSON to the save service
print("Sending data...")
socket.send_json(player_data_payload)

# Wait for response
response = socket.recv_json()
print("Response from save service:", response)
