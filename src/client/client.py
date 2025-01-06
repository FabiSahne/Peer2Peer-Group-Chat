import socket
import threading

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

    def stop(self):
        self.running = False
        self.server_socket.close()
        print("Disconnected from server.")

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
            command = input("Enter command (/broadcast <message>, /quit): ")
            if command.startswith("/broadcast"):
                _, message = command.split(" ", 1)
                client.send_broadcast(message)
            elif command == "/quit":
                break
    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        client.stop()

