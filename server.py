import socket  
import ipaddress  
import time  
from pymongo import MongoClient  
from bson.objectid import ObjectId

maxPacketSize = 1024

# Function to validate the input IP address
def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

# Prompt the user for an IP address to bind the server
ip_address = input("Enter IP address to bind the server: ")
if not validate_ip(ip_address):
    print("Invalid IP address.")
    exit(1)

# Prompt the user for a port number to bind the server
port_input = input("Enter port number to bind the server: ")
try:
    port_number = int(port_input)
    # Ensure the port number is within the valid range
    if not (1024 <= port_number <= 65535):
        raise ValueError
except ValueError:
    print("Invalid port number. Must be between 1024 and 65535.")
    exit(1)

# Connect to MongoDB
client = MongoClient("mongodb+srv://phong:mAyiXVePqgHNyC3U@cluster0.mkom8.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")  # Update your connection string
db = client['test']  # Database
metadata_collection = db['phongDataniz_metadata']
virtual_collection = db['phongDataniz_virtual']

# Calculate the average moisture in the kitchen fridge over the last 3 hours
def choice1(metadata_collection, virtual_collection):
    # Query the Metadata Collection
    metadata = metadata_collection.find_one({"_id": ObjectId("67579109250274380ba04219")})
    parent_asset_uid = metadata.get("assetUid")

    current_time = int(time.time())
    started_time = current_time - (3 * 60 * 60)  # 3 hours ago

    pipeline = [
        {"$match": {"payload.parent_asset_uid": parent_asset_uid, "payload.timestamp": {"$exists": True}}},
        {"$addFields": {"timestamp_as_int": {"$toLong": "$payload.timestamp"}}},
        {"$match": {"timestamp_as_int": {"$gte": started_time}}},
        {"$group": {"_id": None, "averageMoisture": {"$avg": {"$toDouble": "$payload.RH_kitchen"}}}}
    ]

    result = list(virtual_collection.aggregate(pipeline))
    if result:
        return f"\n\nThe average moisture inside my kitchen fridge in the past three hours: {result[0]['averageMoisture']:.2f} RH%.\n"
    else:
        return "\nNo data found for the past 3 hours.\n"

# Calculate the average water consumption per cycle in the smart dishwasher
def choice2(metadata_collection, virtual_collection):
    # Query the Metadata Collection
    metadata = metadata_collection.find_one({"_id": ObjectId("675790e9250274380ba04215")})
    parent_asset_uid = metadata.get("assetUid")

    pipeline = [
        {"$match": {"payload.parent_asset_uid": parent_asset_uid}},
        {"$group": {"_id": None, "averageWaterConsumption": {"$avg": {"$toDouble": "$payload.Water_washer"}}}}
    ]

    result = list(virtual_collection.aggregate(pipeline))
    if result:
        return f"\n\nThe average water consumption per cycle in my smart dishwasher: {result[0]['averageWaterConsumption'] * 0.219969 * 30:.2f} gallons.\n"
    else:
        return "\nNo data found for water consumption.\n"

# Determine the device with the highest energy consumption
def choice3(metadata_collection, virtual_collection):
    # Query the Metadata Collection
    data = virtual_collection.find({}) 
    devices = {}

    for document in data:
        payload = document.get("payload", {})
        voltage = payload.get("Voltage_kitchen") or payload.get("Voltage_washer") or payload.get("Voltage_room")
        current = payload.get("Current_kitchen") or payload.get("Current_washer") or payload.get("Current_room")
        parent_asset_uid = payload.get("parent_asset_uid")
        timestamp = payload.get("timestamp")

        if voltage and current and parent_asset_uid and timestamp:
            power = float(voltage) * float(current)  
            timestamp = int(timestamp)

            if parent_asset_uid in devices:
                devices[parent_asset_uid]["total_power"] += power
                devices[parent_asset_uid]["count"] += 1
                devices[parent_asset_uid]["timestamps"].append(timestamp)
            else:
                devices[parent_asset_uid] = {
                    "total_power": power,
                    "count": 1,
                    "voltage": float(voltage),
                    "current": float(current),
                    "timestamps": [timestamp],
                }

    # Energy consumption for each device
    for device, info in devices.items():
        if len(info["timestamps"]) > 1:
            total_seconds = max(info["timestamps"]) - min(info["timestamps"])
            total_hours = total_seconds / 3600
        else:
            total_hours = 0

        info["total_hours"] = total_hours
        info["energy_consumption"] = (info["total_power"] / info["count"] * total_hours) / 1000

    # Find the device with the highest energy consumption
    max_energy_device = max(devices.items(), key=lambda x: x[1]["energy_consumption"])

    device_doc = metadata_collection.find_one({"assetUid": max_energy_device[0]})
    device_name = device_doc.get("customAttributes", {}).get("name")
    
    return f"\n\nThe device with the highest energy consumption is {device_name} " \
           f"with {max_energy_device[1]['energy_consumption']:.2f} kWh.\n"

# Process client's choice and retrieve data
def extract_data(choice):
    if choice == 1:
        return choice1(metadata_collection, virtual_collection)
    elif choice == 2:
        return choice2(metadata_collection, virtual_collection)
    elif choice == 3:
        return choice3(metadata_collection, virtual_collection)
    else:
        return "Invalid choice."

# Create a TCP socket for server-client communication
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myTCPSocket.bind((ip_address, port_number)) 
myTCPSocket.listen(5) 

print("Server is running and waiting for connections...")

# Handle client connections
try:
    while True:
        incomingSocket, clientAddress = myTCPSocket.accept()  
        print(f"Connection established with {clientAddress}")

        try:
            while True:
                message = incomingSocket.recv(maxPacketSize).decode("utf-8")
                if not message:
                    break

                print(f"Received request from {clientAddress}: {message}")
                print("Processing client's request...")

                try:
                    choice = int(message)  
                except ValueError:
                    response = "Invalid input. Please send a number (1, 2, or 3)."
                    incomingSocket.send(bytearray(response, encoding="utf-8"))
                    continue

                if choice:
                    selected_data = extract_data(choice)
                    response = f"Response: {selected_data}"
                else:
                    response = "No data found in the database."

                incomingSocket.send(bytearray(response, encoding="utf-8"))
                print(f"Sent to {clientAddress}: {response}")
        finally:
            incomingSocket.close()  
except KeyboardInterrupt:
    print("\nShutting down the server.")  
finally:
    myTCPSocket.close() 
