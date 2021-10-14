import socket
import threading
import time

HOST = ''
PORT = 
FORMAT = "utf-8"

clients = []
clients_names = []

def start_server():
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST,PORT))
    print("Starting server")
    
    server.listen(2)
    threading._start_new_thread(accept_clients,(server, " "))
    

def accept_clients(server,m):
    while True:
        if len(clients) < 2:
            client, addr = server.accept()
            print(f"Connection from {addr} established!")
            clients.append(client)
            
            threading._start_new_thread(run_game, (client,addr))
            
# Function to receive/send messages to client
def run_game(client, addr):
    global server, client_name, clients
    
    client_name = client.recv(4096).decode(FORMAT)
    print("Recieved", client_name)
    
    if len(clients) < 2:
        client.send("Welcome Player 1 to the game ".encode(FORMAT))
        client.send("wait".encode(FORMAT))
    else:
        client.send("Welcome Player 2 to the game".encode(FORMAT))
        client.send("wait".encode(FORMAT))

    clients_names.append(client_name)

    if len(clients) > 1:
        symbols = ["O", "X"]
        msg1 = "opponent_name$" + clients_names[1] + "symbol" + symbols[0]
        msg2 = "opponent_name$" + clients_names[0] + "symbol" + symbols[1]
       
        clients[0].send(msg1.encode(FORMAT))
        clients[1].send(msg2.encode(FORMAT))
    

    while True:
        # get the player choice from received data
        data = client.recv(4096).decode(FORMAT)
        print(data)
        
        if not data: break
 
        else: #received a valid position number

            data_send = data.encode(FORMAT)

            if client == clients[0]:
                clients[1].send(data_send)
            else:
                clients[0].send(data_send)
                
    client.close()

start_server()
