"""P2P Server"""
import socket
import threading
import time

"""
Class to represent a client type
"""
class Client:
    def __init__(self, c_ip, c_port, c_nick, c_conn):
        self.ip = c_ip
        self.port = c_port
        self.nick = c_nick,
        self.conn = c_conn


    def send_peer_list(self, peers):
        try:
            print("Sending list of connected peers to client...")
            message = "LIST:" + ":".join(
                f"{connected.nick}:{connected.ip}:{connected.port}" for connected in peers) + "\r\n"
            self.conn.send(message.encode())
        except Exception as e:
            print(f"Error sending peer list: {e}")


class Server:
    """
    Initializes server with given *address* (a 2-tuple (host, port))

    >>> serv = Server(('', 8080))
    """

    def __init__(self, address: tuple[str, int]):
        self.address = address
        self.clients = []

        self.server_socket = socket.create_server(address)

        self.running = True
        threading.Thread(target=self._thread_connection_listener, daemon=True).start()

    def _thread_connection_listener(self):
        while self.running:
            try:
                conn, client_addr = self.server_socket.accept()
                client = Client(None, None, None, conn)
                threading.Thread(target=self._thread_manage_client, args=(client,), daemon=True).start()
                print(f"Connection from {client_addr}")
            except Exception as e:
                print(f"Error connecting: {e}")

    def _thread_manage_client(self, client: Client):
        buffer = ""
        try:
            while True:
                message_chunk = client.conn.recv(1024).decode()
                if not message_chunk:  # disconnected
                    print(f"Connection closed from {client.nick}")
                    self._notify_everyone(f"UPDATE:LEAVE:{client.nick}:{client.ip}:{client.port}\r\n")
                    raise ConnectionError("Connection closed by client.")
                buffer += message_chunk
                while "\r\n" in buffer:
                    message, buffer = buffer.split("\r\n", 1)
                    self.process_message(message, client)
        except Exception as e:
            print(f"Error managing client: {e}")
        finally:
            if client.conn:
                client.conn.close()
            if client in self.clients:
                self.clients.remove(client)
                print(f"{client.nick} disconnected")

    def _notify_everyone(self, message: str):
        print(f"Notifying peers: {message}")
        for client in self.clients:
            try:
                client.conn.send(message.encode())
            except Exception as e:
                print(f"Error while notifying peers: {e}")

    def _register_client(self, message: str, client: Client):
        try:
            print("Registering Client")
            message_parts = message.strip().split(":")
            assert len(message_parts) == 4
            nickname, ip, udp_port = message_parts[1], message_parts[2], int(message_parts[3])

            # TODO: Error handling when nickname already exists

            client.ip = ip
            client.port = udp_port
            client.nick = nickname

            self.clients.append(client)
            self._notify_everyone(f"UPDATE:JOIN:{nickname}:{ip}:{udp_port}\r\n")
            client.send_peer_list(self.clients)

            print(f"{nickname} registered at: {ip}:{udp_port}")

        except Exception as e:
            print(f"Error registering client: {e}")

    def broadcast_message(self, message: str):
        try:
            message_parts = message.strip().split(":")
            assert len(message_parts) >= 4
            nickname, length, msg = message_parts[1], int(message_parts[2]), ":".join(message_parts[3:])
            broadcast_message = f"BROADCAST:{nickname}:{length}:{msg}\r\n"
            self._notify_everyone(broadcast_message)
            print(f"BROADCAST from {nickname}: {msg}")
        except Exception as e:
            print(f"Error broadcasting message: {e}")

    def process_message(self, message: str, client: Client):
        if message.startswith("REGISTER:"):
            self._register_client(message, client)
        elif message.startswith("BROADCAST:"):
            self.broadcast_message(message)
        else:
            print(f"Invalid message recieved: {message}")

    def stop(self):
        self.running = False
        self.server_socket.close()


if __name__ == "__main__":
    server = Server(('', 1337))
    addr, port = server.server_socket.getsockname()
    print(f"Server running on {addr}:{port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Closing server...")
        server.stop()
