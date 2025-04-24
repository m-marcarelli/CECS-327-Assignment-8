import socket
import threading

def receive_messages(client_socket):
    # Continuously receives messages from the server
    while True:
        try:
            response = client_socket.recv(1024).decode()

            if not response:
                print("Server closed the connection.")
                break

            print(f"\nReceived from server: {response}")  # Display server's messages

        except ConnectionResetError:
            print("Server disconnected.")
            break

def send_messages(client_socket):
    # Allows the client to send messages freely
    while True:
        message = input("Enter message to send (or 'exit' to quit): ").strip()

        if message.lower() == 'exit':
            print("Closing connection.")
            client_socket.close()
            break

        client_socket.send(message.encode())
        print(f"Message sent: {message.upper()}")  # Show only the sent message in uppercase

def start_client():
    server_ip = input("Enter server IP address: ")
    port = int(input("Enter server port number: "))

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))
        print(f"Connected to server at {server_ip}:{port}")

        # Start two threads: one for receiving, one for sending
        # Threads used so that client and server do not have to wait for each other, so they can send as many messages as desired whenever
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))

        receive_thread.start()
        send_thread.start()

        receive_thread.join()
        send_thread.join()

    except socket.error as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    start_client()