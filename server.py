# Server.py

# ---------------------------------------------------------------
# This file implements the TCP Server component for the IoT system.

# Responsibilities:
# - Connects to NeonDB to retrieve IoT sensor data
# - Handles queries from the TCP client to:
#     1. Calculate average fridge humidity over the last 3 hours
#     2. Determine average dishwasher water usage per cycle (in gallons)
#     3. Identify the device with the highest electricity consumption (USING A BSF)

# Device metadata is loaded from the "query_table_metadata" table.
# Sensor readings are queried from the "query_table_virtual" table.

# This server expects the client to send query codes: "1", "2", or "3".
# It replies with processed, human-readable answers in imperial units and PST-adjusted timeframes.
# --------------------------------------------------------------- 

# ---------------------------------------------------------------
# Imports
import socket
import psycopg2
from datetime import datetime, timedelta, timezone
import json
import pytz
# ---------------------------------------------------------------
# Connecting to neonDB
def connect_to_db():
    connect = psycopg2.connect("postgresql://neondb_owner:npg_ylIsMtYO84SD@ep-morning-shadow-a4z1nstr-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")
    return connect
# ---------------------------------------------------------------
# MetaData Constants
TABLE_NAME = "query_table_virtual"
FRIDGE = "00r-kzd-al2-8cz"
DISHWASHER = "5kt-0b0-4xx-l5x"
# ---------------------------------------------------------------
# Time Conversion from UTC -> PST
def conersion_to_pst(dt):
    utc = pytz.utc
    pst = pytz.timezone("US/Pacific")
    return utc.localize(dt).astimezone(pst)
# ---------------------------------------------------------------
#Query Handling
def server_query1():
    """Average fridge moisture (sensor1) in past 3 hours"""
    conn = connect_to_db()
    cur = conn.cursor()
    three_hours_ago = datetime.now(timezone.utc) - timedelta(hours=3)
    print("[DEBUG] Looking for fridge data since:", three_hours_ago)

    cur.execute(f"""
        SELECT payload FROM {TABLE_NAME}
        WHERE time >= %s
        """, (three_hours_ago,))
    rows = cur.fetchall()
    moisture_vals = []

    for row in rows:
        payload = row[0]
        if payload.get("parent_asset_uid") == FRIDGE:
            for k, v in payload.items():
                if "moisture" in k.lower():
                    try:
                        moisture_vals.append(float(v))
                    except:
                        continue

    cur.close()
    conn.close()

    if not moisture_vals:
        return "No fridge moisture data found"
    
    avg = sum(moisture_vals) / len(moisture_vals)
    return f"The average moisture in your fridge (past 3 hours) is {avg:.2f} RH&."

def server_query2():
    """Average water usage per dishwasher cycle (in gallons)"""
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(f"SELECT payload from {TABLE_NAME}")
    rows = cur.fetchall()
    water_vals = []

    for row in rows:
        payload = row[0]
        if payload.get("parent_asset_uid") == DISHWASHER:
            for k, v in payload.items():
                if "water" in k.lower():
                    try:
                        liters = float(v)
                        gallons = liters * 0.264172
                        water_vals.append(gallons)
                    except:
                        continue
    cur.close()
    conn.close()

    if not water_vals:
        return "No dishwasher water usage data found."
    
    avg = sum (water_vals) / len(water_vals)
    return f"The average water per dishwasher cycle is {avg:.2f} gallons."

class BSTNode:
    def __init__(self, key, value):
        self.key = key      # electricity usage
        self.value = value  # device name
        self.left = None
        self.right = None

    def insert(self, key, value):
        if key < self.key:
            if self.left:
                self.left.insert(key, value)
            else:
                self.left = BSTNode(key, value)
        else:
            if self.right:
                self.right.insert(key, value)
            else:
                self.right = BSTNode(key, value)

    def find_max(self):
        if self.right:
            return self.right.find_max()
        return self.key, self.value

def server_query3():
    """Copare electricity usage using BST"""
    conn = connect_to_db()
    cur = conn.cursor()

    cur.execute(f"SELECT payload from {TABLE_NAME}")
    rows = cur.fetchall()
    device_usage = {}

    for row in rows:
        payload = row[0]
        uid = payload.get("parent_asset_uid")
        if uid == FRIDGE:
            for k, v in payload.items():
                if "moisture" in k.lower():
                    try:
                        device_usage["Fridge"] = device_usage.get("Fridge", 0) + float (v)
                    except:
                        continue

        elif uid == DISHWASHER:
            for k, v in payload.items():
                if "acs" in k.lower():
                    try:
                        device_usage['Dishwasher'] = device_usage.get("Dishwasher", 0) + float(v)
                    except:
                        continue

    cur.close()
    conn.close()

    root = None
    for device, usage in device_usage.items():
        if root is None:
            root = BSTNode(usage, device)
        else:
            root.insert(usage, device)

    if root:
        max_usage, device = root.find_max()
        return f"{device} consumed the most electricity: {max_usage:.2f} kWh."
    else:
        return "No electricity data available to compare"
# ---------------------------------------------------------------
#TCP Server
def TCP_server():
    try:
        server_port = int(input("Enter server port number:"))

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_socket.bind(('0.0.0.0', server_port))
        server_socket.listen(5)

        print(f"[SERVER] Server is listening on port {server_port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"[SERVER]Connected to {client_address}")

            while True:
                data = client_socket.recv(1024)
                if not data:
                    print("[SERVER] Client disconnected.")
                    break

                query_code = data.decode().strip()
                print(f"[SERVER] Recieved query code: {query_code}")

                if query_code == "1":
                    response = server_query1()
                elif query_code == "2":
                    response = server_query2()
                elif query_code == "3":
                    response = server_query3()

                client_socket.sendall(response.encode())

            client_socket.close()

    except ValueError:
        print("[ERROR] Invalid port number.")
    finally:
        if 'server_socket' in locals():
            server_socket.close()
        print("[SERVER] Server shut down.")
    
# ---------------------------------------------------------------
# Main
if __name__ == "__main__":
    TCP_server()
    
# ---------------------------------------------------------------
