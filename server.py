import socket
import threading
import psycopg2
from datetime import datetime, timedelta
import json

# Funct to connect to NeonDB
def connect_to_db():
    connect = psycopg2.connect("postgresql://neondb_owner:npg_Cu7tJmQbGNg4@ep-calm-lake-a5oj4a07-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    return connect

# Implement binary search tree 
class DeviceBST:
    def __init__(self):
        self.root = None

    def insert(self, device_id, metadata):
        self.root = self._insert_recursive(self.root, device_id, metadata)

    def _insert_recursive(self, node, device_id, metadata):
        if node is None:
            return DeviceNode(device_id, metadata)
        if device_id < node.device_id:
            node.left = self._insert_recursive(node.left, device_id, metadata)
        else:
            node.right = self._insert_recursive(node.right, device_id, metadata)
        return node

    def find(self, device_id):
        return self._find_recursive(self.root, device_id)

    def _find_recursive(self, node, device_id):
        if node is None:
            return None
        if node.device_id == device_id:
            return node.metadata
        if device_id < node.device_id:
            return self._find_recursive(node.left, device_id)
        else:
            return self._find_recursive(node.right, device_id)

# Insert devices into BST using metadata in neon
def build_device_tree(conn):
    bst = DeviceBST()
    cursor = conn.cursor()

    cursor.execute('SELECT assetUid, assetType, customAttributes FROM "Table 1_metadata"')

    for row in cursor.fetchall():
        device_id = row[0]
        device_type = row[1]
        custom_attrs = row[2]

        # Ensure the JSON is a dictionary
        if isinstance(custom_attrs, str):
            custom_attrs = json.loads(custom_attrs)

        name = custom_attrs.get("name", "Unnamed Device")
        timezone = "UTC"  # Set default; convert to PST later
        unit = None

        try:
            boards = custom_attrs["children"]
            for board in boards:
                sensors = board["customAttributes"]["children"]
                for sensor in sensors:
                    u = sensor["customAttributes"].get("unit")
                    if u:
                        unit = u
                        break
        except KeyError:
            pass

        metadata = {
            "device_id": device_id,
            "name": name,
            "type": device_type,
            "unit": unit,
            "timezone": timezone
        }

        bst.insert(device_id, metadata)

    cursor.close()
    return bst
        
# Singular device node
class DeviceNode:
    def __init__(self, device_id, metadata):
        self.device_id = device_id
        self.metadata = metadata
        self.left = None
        self.right = None

def handle_client(client_socket, conn, device_tree):
    while True:
        try:
            data = client_socket.recv(1024).decode()

            if not data:
                print("Client disconnected.")
                break

            print(f"Received query from client: {data}")

            if data == "1":
                response = handle_query_1(conn, device_tree)
            elif data == "2":
                response = handle_query_2(conn, device_tree)
            elif data == "3":
                response = handle_query_3(conn, device_tree)
            else:
                response = "Invalid query number."

            client_socket.send(response.encode())

        except ConnectionResetError:
            print("Client forcefully disconnected.")
            break

    client_socket.close()

def handle_query_1(conn, device_tree):
    device_id = "m38-e25-320-1z8"  # Fridge 1 device ID
    cursor = conn.cursor()

    # Get the current UTC time and compute 3 hours ago
    three_hours_ago = int((datetime.now(datetime.timezone.utc) - timedelta(hours=3)).timestamp())

    cursor.execute("""
        SELECT payload
        FROM "Table 1_virtual"
        WHERE payload ->> 'parent_asset_uid' = %s
    """, (device_id,))

    rows = cursor.fetchall()

    moisture_readings = []

    for row in rows:
        payload = row[0]

        if isinstance(payload, str):
            payload = json.loads(payload)

        try:
            timestamp = int(payload.get("timestamp", "0"))
            if timestamp >= three_hours_ago:
                raw_val = payload.get("Moisture Meter - Moisture Meter")
                if raw_val:
                    moisture = float(raw_val)
                    moisture_readings.append(moisture)
        except Exception:
            continue

    cursor.close()

    if not moisture_readings:
        return "No recent moisture readings found."

    avg_moisture = sum(moisture_readings) / len(moisture_readings)
    rh_percent = avg_moisture  # Assuming 0–100 scale

    return f"Average Relative Humidity inside your fridge over the last 3 hours is: {rh_percent:.2f}%"

def send_messages(client_socket):
    # Allows the server to send messages to the client manually
    while True:
        message = input("Enter message to send to client (or 'exit' to quit): ").strip()

        if message.lower() == 'exit':
            print("Closing connection.")
            client_socket.close()
            break

        client_socket.send(message.encode())
        print(f"Message sent to client: {message}")

def handle_query_2(conn, device_tree):
    device_id = "392-szf-z5u-bh0"  # Smart Dishwasher UID
    cursor = conn.cursor()

    cursor.execute("""
        SELECT payload
        FROM "Table 1_virtual"
        WHERE payload ->> 'parent_asset_uid' = %s
    """, (device_id,))

    rows = cursor.fetchall()
    water_readings_cups = []

    for row in rows:
        payload = row[0]
        if isinstance(payload, str):
            payload = json.loads(payload)

        try:
            raw_val = payload.get("Smart Dishwasher Consumption Sensor")
            if raw_val:
                water_cups = float(raw_val)
                water_readings_cups.append(water_cups)
        except Exception:
            continue

    cursor.close()

    if not water_readings_cups:
        return "No water usage data found for dishwasher."

    avg_cups = sum(water_readings_cups) / len(water_readings_cups)
    avg_gallons = avg_cups / 16  # Convert cups to gallons

    return f"Average water consumption per cycle for your dishwasher: {avg_gallons:.2f} gallons."

def start_server():
    port = int(input("Enter the port number for the server: "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Server is listening on port {port}...")

    conn = connect_to_db()
    device_tree = build_device_tree(conn)

    client_socket, client_address = server_socket.accept()
    print(f"Connected to client: {client_address}")

    handle_client(client_socket, conn, device_tree)

    conn.close()

if __name__ == "__main__":
    start_server()