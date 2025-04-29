# Client.py
# ---------------------------------------------------------------
# This file implements the TCP Client component for the IoT system.

# Responsibilities:
# - Connects to the TCP Server using user-specified IP address and port number
# - Displays a menu of valid queries to the user
# - Sends selected query codes ("1", "2", or "3") to the server
# - Receives and displays processed results from the server

# Valid Queries:
# 1. What is the average moisture inside my kitchen fridge in the past three hours?
# 2. What is the average water consumption per cycle in my smart dishwasher?
# 3. Which device consumed more electricity among my three IoT devices?

# The client runs continuously until the user types 'exit'.
# ---------------------------------------------------------------
# Imports
import socket
# ---------------------------------------------------------------
# Client functionality
def TCP_client():
    try:
        # get server ip and port from the user
        server_ip = input("Enter server IP address: ")
        server_port = int(input("Enter server port number: "))

        # create tcp socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # connect to the server
        client_socket.connect((server_ip, server_port))
        
        # queries
        valid_queries = [
            "What is the average moisture inside my kitchen fridge in the past three hours?",
            "What is the average water consumption per cycle in my smart dishwasher?",
            "Which device consumed more electricity among my three IoT devices?"
        ]

        while True:
            # show valid queries
            print("\nAvailable queries:")
            for i, query in enumerate(valid_queries, 1):
                print(f"{i}. {query}")
            print("Type 'exit' to disconnect.\n")

            # user input
            message = input("Enter your query number: ")

            # exit
            if message.lower() == 'exit':
                print("Closing connection...")
                break

            # validate query
            if message in ['1', '2', '3']:
                client_socket.send(bytearray(str(message), encoding='utf-8'))
                server_response = client_socket.recv(1024)
                print("Server response:", server_response.decode())
            else:
                print("\nSorry, this query cannot be processed. Please try one of the following options:")
                for query in valid_queries:
                    print(f"- {query}")
                
    except ValueError:
        print("Error: Invalid port number.")
    except socket.gaierror:
        print("Error: Invalid IP or server unreachable.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
# ---------------------------------------------------------------
# Main
if __name__ == "__main__":
    TCP_client()
# ---------------------------------------------------------------
