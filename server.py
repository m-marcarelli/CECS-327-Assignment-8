import socket
import threading
import psycopg2
from datetime import datetime, timedelta

# Funct to connect to NeonDB
def connect_to_db():
    connect = psycopg2.connect("postgresql://neondb_owner:npg_Cu7tJmQbGNg4@ep-calm-lake-a5oj4a07-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require")
    return connect

def handle_client(client_socket):
    # Receives messages from client and displays them (without capitalization)
    while True:
        try:
            # Receive message from client
            data = client_socket.recv(1024).decode()

            if not data:
                print("Client disconnected.")
                break

            print(f"Received from client: {data}")  # Show original message from client

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