import socket
import threading
import json

class Client:
    def __init__(self, ip, port, username, client_ip, udp_port):
        self.ip = ip
        self.port = port
        self.username = username
        self.client_ip = client_ip
        self.udp_port = udp_port
        
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True
        self.peers = {}
        
        self.chat_sessions = {}
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((client_ip, udp_port))
        
        self.tcp_listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_listener.bind((client_ip, 0))
        self.tcp_port = self.tcp_listener.getsockname()[1]
        self.tcp_listener.listen(5)

        threading.Thread(target=self.udp_listener, daemon=True).start()
        threading.Thread(target=self.tcp_connection_listener, daemon=True).start()

    def connect_to_server(self):
        try:
            self.server_socket.connect((self.ip, self.port))
            register_message = f"REGISTER:{self.username}:{self.client_ip}:{self.udp_port}\r\n"
            self.server_socket.send(register_message.encode())
            print(f"Connected to server as {self.username}")

            threading.Thread(target=self.server_listener, daemon=True).start()
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def server_listener(self):
        buffer = ""
        try:
            while self.running:
                chunk = self.server_socket.recv(1024).decode()
                if not chunk:
                    print("Disconnected from server.")
                    break

                buffer += chunk

                while "\r\n" in buffer:
                    message, buffer = buffer.split("\r\n", 1)
                    self.process_server_message(message)
        except Exception as e:
            print(f"Error in server listener: {e}")
        finally:
            self.running = False

    def process_server_message(self, message):
        if message.startswith("LIST:"):
            self.update_peer_list(message)
        elif message.startswith("UPDATE:JOIN:") or message.startswith("UPDATE:LEAVE:"):
            self.update_peer_status(message)
        elif message.startswith("BROADCAST:"):
            self.display_broadcast(message)
        else:
            print(f"Unknown message from server: {message}")

    def update_peer_list(self, message):
        try:
            self.peers = {}
            parts = message.split(":")[1:]
            for i in range(0, len(parts), 3):
                nickname, ip, port = parts[i], parts[i + 1], int(parts[i + 2])
                self.peers[nickname] = (ip, port)
            print(f"Updated peer list: {self.peers}")
        except Exception as e:
            print(f"Failed to update peer list: {e}")

    def update_peer_status(self, message):
        try:
            parts = message.split(":")
            action, nickname, ip, port = parts[1], parts[2], parts[3], int(parts[4])
            if action == "JOIN":
                self.peers[nickname] = (ip, port)
                print(f"{nickname} joined the chat.")
            elif action == "LEAVE":
                if nickname in self.peers:
                    del self.peers[nickname]
                print(f"{nickname} left the chat.")
        except Exception as e:
            print(f"Failed to update peer status: {e}")

    def display_broadcast(self, message):
        try:
            parts = message.split(":")
            nickname = parts[1]
            length = int(parts[2])
            content = ":".join(parts[3:])[:length]
            print(f"Broadcast from {nickname}: {content}")
        except Exception as e:
            print(f"Failed to display broadcast: {e}")

    def send_broadcast(self, content):
        try:
            message = f"BROADCAST:{self.username}:{len(content)}:{content}\r\n"
            self.server_socket.send(message.encode())
            print(f"Broadcast sent: {content}")
        except Exception as e:
            print(f"Failed to send broadcast: {e}")

    def udp_listener(self):
        while self.running:
            try:
                data, addr = self.udp_socket.recvfrom(1024)
                message = json.loads(data.decode())
                
                if message["type"] == "tcp_port_info":
                    peer_username = message["username"]
                    peer_tcp_port = message["tcp_port"]
                    print(f"Received TCP port {peer_tcp_port} from {peer_username}")
                    self.connect_to_peer(peer_username, addr[0], peer_tcp_port)
                    
            except Exception as e:
                print(f"Error in UDP listener: {e}")

    def tcp_connection_listener(self):
        while self.running:
            try:
                client_socket, address = self.tcp_listener.accept()
                peer_username = client_socket.recv(1024).decode()
                print(f"Accepted connection from {peer_username}")
                self.create_chat_session(peer_username, client_socket)
            except Exception as e:
                print(f"Error in TCP connection listener: {e}")

    def initiate_chat(self, peer_username):
        if peer_username not in self.peers:
            print(f"Peer {peer_username} not found")
            return
            
        if peer_username in self.chat_sessions:
            print(f"Chat session with {peer_username} already exists")
            return
            
        peer_ip, peer_udp_port = self.peers[peer_username]
        
        message = {
            "type": "tcp_port_info",
            "username": self.username,
            "tcp_port": self.tcp_port
        }
        
        try:
            self.udp_socket.sendto(json.dumps(message).encode(), (peer_ip, peer_udp_port))
            print(f"Sent TCP port info to {peer_username}")
        except Exception as e:
            print(f"Failed to send TCP port info: {e}")

    def connect_to_peer(self, peer_username, peer_ip, peer_tcp_port):
        try:
            peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peer_socket.connect((peer_ip, peer_tcp_port))
            peer_socket.send(self.username.encode())
            self.create_chat_session(peer_username, peer_socket)
        except Exception as e:
            print(f"Failed to connect to peer {peer_username}: {e}")

    def create_chat_session(self, peer_username, socket):
        self.chat_sessions[peer_username] = socket
        threading.Thread(
            target=self.handle_peer_messages,
            args=(peer_username, socket),
            daemon=True
        ).start()

    def handle_peer_messages(self, peer_username, socket):
        try:
            while self.running:
                message = socket.recv(1024).decode()
                if not message:
                    break
                print(f"Message from {peer_username}: {message}")
        except Exception as e:
            print(f"Error in peer message handler for {peer_username}: {e}")
        finally:
            self.close_chat_session(peer_username)

    def send_peer_message(self, peer_username, message):
        if peer_username not in self.chat_sessions:
            print(f"No active chat session with {peer_username}")
            return False
            
        try:
            self.chat_sessions[peer_username].send(message.encode())
            return True
        except Exception as e:
            print(f"Failed to send message to {peer_username}: {e}")
            self.close_chat_session(peer_username)
            return False

    def close_chat_session(self, peer_username):
        if peer_username in self.chat_sessions:
            try:
                self.chat_sessions[peer_username].close()
            except:
                pass
            del self.chat_sessions[peer_username]
            print(f"Chat session with {peer_username} closed")

    def stop(self):
        self.running = False
        
        for peer_username in list(self.chat_sessions.keys()):
            self.close_chat_session(peer_username)
            
        self.udp_socket.close()
        self.tcp_listener.close()
        self.server_socket.close()
        print("Disconnected from server and peers.")

if __name__ == "__main__":
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))
    username = input("Enter your username: ")
    client_ip = input("Enter your client IP: ")
    client_udp_port = int(input("Enter your UDP port: "))

    client = Client(server_ip, server_port, username, client_ip, client_udp_port)
    client.connect_to_server()

    try:
        while True:
            command = input("Enter command (/broadcast <message>, /chat <username> <message>, /start <username>, /quit): ")
            if command.startswith("/broadcast"):
                _, message = command.split(" ", 1)
                client.send_broadcast(message)
            elif command.startswith("/chat"):
                _, username, message = command.split(" ", 2)
                client.send_peer_message(username, message)
            elif command.startswith("/start"):
                _, username = command.split(" ", 1)
                client.initiate_chat(username)
            elif command == "/quit":
                break
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        client.stop()

