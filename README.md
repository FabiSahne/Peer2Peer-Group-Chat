# P2P Chat Application

## How Communication Works

The communication system leverages the following mechanisms:

    Server:
        Acts as a registry where clients can register themselves.
        Maintains and shares a list of active peers with all connected clients.
        Relays broadcast messages to all registered clients.

    Client:
        Registers with the server and retrieves the list of other connected peers.
        Can send and receive broadcast messages through the server.
        Initiates direct communication with other peers for private chat using UDP and TCP.

## Code Breakdown
### Server

The server provides centralized functionality, including:

    Managing a list of connected clients.
    Relaying broadcast messages.
    Notifying peers about join/leave events.

Key Functions:

    _register_client:
        Handles the REGISTER messages from clients.
        Updates the list of connected peers and notifies others of the new client.

    _broadcast_message:
        Distributes broadcast messages received from clients to all other clients.

    _notify_everyone:
        Sends a specified message to all connected clients.

    Socket Listener:
        Continuously listens for incoming client connections using the accept method of the server socket.

### Client

The client implements both centralized and decentralized communication:

    Centralized Communication:
        Registers itself with the server and receives a list of peers.
        Broadcasts messages to all peers via the server.
    Decentralized Communication:
        Sends direct messages to peers using a combination of UDP (to share connection details) and TCP (for message exchange).

Key Components:

    Registration:
        Sends a REGISTER message to the server containing its username, IP, and UDP port.
        Receives the list of active peers in response.

    Broadcast Messaging:
        Sends broadcast messages to the server, which relays them to other connected clients.

    Direct Messaging:
        Initiates a private chat with a peer by first exchanging TCP port details over UDP.
        Establishes a TCP connection to exchange private messages.

Threads:

    UDP Listener:
        Monitors incoming UDP messages for peer details.
    TCP Listener:
        Listens for incoming TCP connections from peers.
    Server Listener:
        Handles messages from the server.
    Peer Message Handler:
        Manages incoming private messages from peers.

### Chat Workflow:

    Initialization:
        A client registers with the server, providing its IP and UDP port.
        The server responds with the list of active peers.

    Broadcasting:
        The client sends a message to the server for broadcast.
        The server relays the message to all connected peers.

    Private Chat:
        A client sends its TCP port details to a peer via UDP.
        The peer uses the provided details to establish a TCP connection.
        The two peers exchange messages directly over the TCP connection.

    Disconnecting:
        When a client disconnects, it notifies the server, which updates the peer list and informs other clients.

### Sample Communication Flow
1. Registration

    Client:
        Sends REGISTER:<username>:<IP>:<UDP port> to the server.
    Server:
        Acknowledges registration and broadcasts the new client details to all peers.

2. Broadcast

    Client:
        Sends BROADCAST:<username>:<message length>:<message> to the server.
    Server:
        Relays the message to all other clients.

3. Private Chat

    Initiating Client:
        Sends its TCP port details to the target peer using UDP.
    Target Peer:
        Establishes a TCP connection to the initiating client.
    Both Peers:
        Exchange messages over the established TCP connection.

## Usage
### Server

    Run the server:

    python server.py

    The server listens on port 1337 by default.

### Client

    Run the client:

    python client.py

    Provide the server IP, port, username, client IP, and UDP port when prompted.
    Use the following commands:
        /broadcast <message>: Send a broadcast message.
        /start <username>: Initiate a private chat.
        /chat <username> <message>: Send a private message.
        /quit: Disconnect from the server and peers.

### Communication Protocols

    UDP:
        Lightweight, used for exchanging connection details (e.g., TCP port numbers).
        Faster but less reliable compared to TCP.

    TCP:
        Reliable, used for private chat and server communication.
        Ensures messages are delivered in order.
