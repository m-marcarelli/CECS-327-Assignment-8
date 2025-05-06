# CECS 327 Assignment 8 - Building an End-to-End IoT System
Marissa Marcarelli & Estefania Perez

## Overview
This project implements an end-to-end IoT system that connects virtual devices from Dataniz to a NeonDB database via a TCP client-server architecture. Users can send predefined queries through a Python-based client to retrieve and analyze real-time sensor data. The server processes each query using metadata, performs calculations and unit conversions, and returns results in user-friendly format. The system integrates IoT concepts, database interaction, socket programming, and metadata utilization.

## Requirements to Run and Compile
- Two cloud VMs
- Python
- `client.py` and `server.py` files

## Windows VM Details

### Setup

Utilize Google Cloud to create two individual VM instances.

#### When creating each instance, ensure to:
- Select `Windows Server 2019 Datacenter, Server with Desktop
Experience` as your Boot Disk. 
- Set your firewall to `Allow HTTP Traffic`. 

#### After creating each instance, ensure to do this on both:

Allow HTTP Traffic:
- Run your VM
- Go into advanced security settings
- Set an inbound rule to allow TCP traffic on certain ports

Install necessary packages and librareis.
- Ensure `python`, `psycopg`, and `pytz` are installed on each VM.
    - Do this by running the following commands in this order:
        ```bash
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe" -OutFile "python-installer.exe"
        ```

        ```bash
        Start-Process "python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_pip=1" -Wait
        ```

        ```bash
        python --version
        ```

        ```bash
        pip --version
        ```

        ```bash
        pip install psycopg2-binary
        ```

        ```bash
        pip install pytz
        ```

## Installing Files 

#### To gain access to the code in your VMs:
- Copy the `client.py` and `server.py` files. In one VM, paste the contents of client into a file and name it accordingly. In the other, paste the contents of server and name it accordingly. Put them in your desired location. 
    - Ex: documents/CECS/CECS 327/Assignment 8/

## How to Run 

### Server setup
Open Windows powershell as an admin on the VM that contains server.py

Then, use the following commands in the following order:

1. Navigate to the location where `server.py` is located on the device:

    ```bash
    cd /path/to/directory
    ```

2. Start the server:

    ```bash
    python server.py
    ```

4. Set the port:

    ```bash
    Enter the port number for the server: (enter a port number that is accepted based on your inbound rule)
    ```

### Client setup
Open Windows powershell as an admin on the VM that contains client.py

Then, use the following commands in the following order:

1. Navigate to the location where `client.py` is located on the device:

    ```bash
    cd /path/to/directory
    ```

2. Start the client:

    ```bash
    python server.py
    ```

3. Connect to the Server's IP:
    
    ```bash
    Enter server IP address: (The IP can be found on google cloud under the servers VM instance)
    ```

4. Connect to the port:

    ```bash
    Enter server port number: (The port that was set by the client)
    ```

### Expected outputs

The server and client programs are now set up and connected. Outputs should be as follows:

#### Server

```bash
Server is listening on port (port)...
Connected to client: ('IP', dynamic port)
```

#### Client

```bash
Connected to server at IP:Port

Available queries:
1. What is the average moisture inside my kitchen fridge in the past three hours?
2. What is the average water consumption per cycle in my smart dishwasher?
3. Which device consumed more electricity among my three IoT devices?
Type 'exit' to disconnect.

Enter your query number:
```

### Querying and communication

The client can now send a query request to the server and recieve an answer back.

Simply enter your desired number and the server will send you back the corresponding answer

### Exiting
To exit the simulation, simply follow the prompt as follows:

```bash
Type 'exit' to disconnect.
```

This will terminate the client. The server will be notified. 