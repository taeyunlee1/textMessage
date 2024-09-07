import socket
import threading
import sys 
import argparse
import threading
from datetime import datetime, timedelta


active_clients = {}

def configure():
    parser = argparse.ArgumentParser(prog='server',
                                              description='Initiates a server',
                                              epilog='Start server using specified port and passcode.')
    parser.add_argument("-start", action="store_true", help="Initiate the server.")
    parser.add_argument('-port', type=int, help='Server port number.')
    parser.add_argument('-passcode', type=str, help='Server access passcode.')

    # Extract and process command-line arguments
    args = parser.parse_args()

    if args.start:  
        if len(args.passcode.strip()) > 5:
            sys.stdout.flush()
            return -1, -1
        return args.port, args.passcode
    else:
        sys.stdout.flush() 
        return -1, -1

def start_server(ip: str, port: int):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(0)
    print(f"Server started on port {port}. Accepting connections")
    sys.stdout.flush()
    return server_socket


def manage_client(client, address, passcode, port, username):

    print(f"{username} joined the chatroom")
    sys.stdout.flush()
    for other_username, other_client in active_clients.items():
        if other_client != client:
            other_client.send(f"{username} joined the chatroom".encode())
    active_clients[username] = client
    while True:
        isDM = False
        message = client.recv(1024).decode()
        if len(message) > 20:
            continue
        elif message == ":Exit":
            print(f"{username} left the chatroom")
            client.close()
            del active_clients[username]
            for other_username, other_client in active_clients.items():
                if other_client != client:
                    other_client.send(f"{username} left the chatroom".encode())      
            break
        elif message == ":mytime":
            time = datetime.now()
            message = str(time.strftime("%a %b %d %H:%M:%S %Y"))
        elif message == ":+1hr":
            time = datetime.now() + timedelta(hours=1)
            message = str(time.strftime("%a %b %d %H:%M:%S %Y"))
        elif message.startswith(':dm'):
            isDM = True
            _, receiver_username, *dm_message = message.split(' ', 2)
            dm_message = ' '.join(dm_message)
            if receiver_username in active_clients:
                receiver_socket = active_clients[receiver_username]
                receiver_socket.send(f'{username}: {dm_message}'.encode())
                print(f'{username} to {receiver_username}: {dm_message}')
                sys.stdout.flush()

        if not isDM:
            print(f'{username}: {message}')
            sys.stdout.flush()
            for other_username, other_client in active_clients.items():
                if other_client != client:
                    other_client.send(f'{username}: {message}'.encode())
                    sys.stdout.flush()

port, passcode = configure()
if port != -1:
    server = start_server("127.0.0.1", port)
    while True:
        client, client_address = server.accept()
        client.send("1".encode())
        client_passcode = client.recv(100).decode()
        if passcode != client_passcode:
             client.send("Incorrect passcode"[:1024].encode()) 
             client.close()
             continue
        else:
            client.send(f"Connected to {client_address[0]} on port {port}"[:1024].encode())
            username = client.recv(1024).decode()
            threading.Thread(target=manage_client, args=(client, client_address, passcode, port, username)).start()

# if __name__ == "__main__":
# 	pass
