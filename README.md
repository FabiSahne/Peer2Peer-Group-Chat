# P2P Group Chat Protocol

## Protocol Overview

### **1. TCP: Client-Server Communication**
- **REGISTER**:
  - **Purpose**: Register a new client with the server.
  - **Format**: `REGISTER:Nickname:IP-Address:UDP-Port\r\n`
  - **Description**:
    - Sent by the client to register itself.
    - Includes the client's nickname, IP address, and UDP port.

- **BROADCAST**:
  - **Purpose**: Send a broadcast message to all connected clients.
  - **Format**: `BROADCAST:Nickname:Length:Message\r\n`
  - **Description**:
    - The client sends a message to the server.
    - The server forwards the message to all other clients.

- **LIST**:
  - **Purpose**: Retrieve the current list of participants.
  - **Format**: `LIST:x times - Nickname:IP-Address:UDP-Port\r\n`
  - **Description**:
    - Sent by the server to the client after registration.

- **UPDATE**:
  - **Purpose**: Notify clients about participant list changes (e.g., join or leave).
  - **Format**: `UPDATE:Action(JOIN, LEAVE):Nickname:IP-Address:UDP-Port\r\n`
  - **Description**:
    - The server notifies all clients about changes to the participant list.

- **ERROR**:
  - **Purpose**: Communicate errors.
  - **Format**: `ERROR:Length:Message\r\n`
  - **Description**:
    - The server informs the client about errors.

---

### **2. UDP: Client-Client Communication**
- **INIT**:
  - **Purpose**: Initialize a direct peer-to-peer connection.
  - **Format**: `INIT:Secret:TCP-Port\r\n`
  - **Description**:
    - A client sends its TCP port information (for P2P) to another client.

- **ACK**:
  - **Purpose**: Acknowledge a P2P connection request.
  - **Format**: `ACK:INIT:Secret\r\n`
  - **Description**:
    - The receiving client confirms the receipt of the `INIT` message.

---

### **3. TCP: Client-Client Communication**
- **CHAT**:
  - **Purpose**: Send a chat message in a P2P session.
  - **Format**: `CHAT:Length:Message\r\n`
  - **Description**:
    - The message length is specified to ensure correct processing.

---

## Implementation Details

### **Server (`server.py`)**
- **Responsibilities**:
  - Manage the participant list.
  - Forward broadcast messages.
  - Notify clients of join/leave events.

### **Client (`client.py`)**
- **Responsibilities**:
  - Register with the server.
  - Retrieve the participant list.
  - Send and receive broadcast messages.
  - Initiate P2P connections via UDP.
  - Directly chat with other clients over TCP.
