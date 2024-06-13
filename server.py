import socket
import threading
import random
import time
import protocol


class GameServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen()
        print(f"Server started on {host}:{port}")

        self.clients = []
        self.active_clients = []
        self.random_seed = random.randint(1, 1000)
        self.start = False
        self.players_id_name = {}
        self.players_sock_id = {}
        self.places = []
        self.start_time = None
        self.speed_time = 0.7

    def broadcast_all(self, name, data):
        for client in self.clients:
            try:
                client.send(protocol.build_message(name, data))
            except:
                print("Removed client")
                self.clients.remove(client)

    def broadcast_all_others(self, from_client, name, data):
        for client in self.clients:
            if client != from_client:
                try:
                    client.send(protocol.build_message(name, data))
                except:
                    self.clients.remove(client)

    def broadcast(self, to_client, message):
        try:
            to_client.send(message)
        except:
            self.clients.remove(to_client)

    def handle_client(self, client, address):
        # Assign a unique ID to the client
        id = random.randint(1, 1000)
        while id in self.players_id_name:
            id = random.randint(1, 1000)

        self.players_sock_id[client] = id
        start_sent = False

        while True:
            try:
                name, data = protocol.receive_data(client)

                if name == "UpdateGrid":
                    self.broadcast_all_others(client, name, {self.players_sock_id[client]: data})

                elif name == "UpdateRows":
                    if int(data) > 1 and len(self.clients) > 1:
                        amount = 0
                        if int(data) == 4:
                            amount = 4
                        elif int(data) == 3:
                            amount = 2
                        elif int(data) == 2:
                            amount = 1

                        selected_client = random.choice(self.clients)
                        while selected_client == client:
                            selected_client = random.choice(self.clients)
                        self.broadcast(selected_client, protocol.build_message(name, str(amount)))

                elif name == "StartGame":
                    if len(self.clients) > 1:
                        self.start = True

                elif name == "GetSeed":
                    self.broadcast(client, protocol.build_message("SetSeed", str(self.random_seed)))

                elif name == "GetPlayers":
                    self.broadcast_all("SetPlayers", self.players_id_name)

                elif name == "SetName":
                    self.players_id_name[id] = data

                if self.start and not start_sent:
                    self.broadcast_all("StartGame", "")
                    start_sent = True

                elif name == "LostGame":
                    self.broadcast_all_others(client, "DelPlayer", str(id))
                    self.active_clients.remove(client)
                    self.places.append(self.players_id_name[id])

                    if len(self.active_clients) <= 1:
                        try:
                            self.places.append(self.players_id_name[self.players_sock_id[self.active_clients[0]]])
                        except:
                            print("Bad")

                        self.broadcast_all("SetPlaces", self.places[::-1])
                        self.broadcast_all("EndGame", "")
                        print("Restarting game")
                        self.reset_game()

                elif name == "EndGame":
                    self.start = False
                    start_sent = False

            except:
                client.close()
                self.clients.remove(client)
                break

        self.cleanup_client(client, id)
        print(f"Client {address} disconnected")

    def update_speed(self):
        time_break = 30
        self.start_time = time.time()
        last_change = 0

        while True:
            if time.time() - self.start_time >= last_change + time_break:
                if self.speed_time > 0.2:
                    self.speed_time -= 0.1
                elif self.speed_time > 0.02:
                    self.speed_time -= 0.01
                last_change += time_break
                self.broadcast_all("SetSpeed", str(self.speed_time))

    def reset_game(self):
        self.start = False
        self.speed_time = 0.7
        self.random_seed = random.randint(1, 1000)
        self.active_clients = self.clients.copy()
        self.places = []

    def cleanup_client(self, client, id):
        self.broadcast_all("DelPlayer", str(id))
        del self.players_id_name[id]
        self.broadcast_all("SetPlayers", self.players_id_name)

    def run(self):
        threading.Thread(target=self.update_speed).start()

        while True:
            client, address = self.sock.accept()
            print(f"Connection from {address}")
            self.clients.append(client)
            self.active_clients.append(client)
            threading.Thread(target=self.handle_client, args=(client, address)).start()


if __name__ == '__main__':
    GameServer().run()