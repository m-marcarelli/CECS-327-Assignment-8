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

def start_server():
    port = int(input("Enter the port number for the server: "))

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Server is listening on port {port}...")

    client_socket, client_address = server_socket.accept()
    print(f"Connected to client: {client_address}")

    # Start two threads: one for handling client messages, one for manual input
    # Threads used so that client and server do not have to wait for each other, so they can send as many messages as desired whenever
    receive_thread = threading.Thread(target=handle_client, args=(client_socket,))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    receive_thread.start()
    send_thread.start()

    receive_thread.join()
    send_thread.join()

if __name__ == "__main__":
    start_server()