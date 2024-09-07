import socket
import threading
import sys
import threading
import argparse
from datetime import datetime, timedelta

def setup_parser():
	parser = argparse.ArgumentParser(
		prog = 'server',
		description = 'Set up server connection',
		epilog = 'Use the port and passcode to create a connection with server.'
	)
	
	parser.add_argument('-join', action='store_true', help = 'Joined the server ')
	parser.add_argument('-host', type=str)
	parser.add_argument('-port', type=int)
	parser.add_argument('-username', type=str)
	parser.add_argument('-passcode', type=str)

	args = parser.parse_args()

	if args.join:
		if len(args.username.strip()) > 8:
			print("Invalid: Display name longer than 8 characters")
			return -1, -1, -1, -1
		return args.host, args.port, args.username, args.passcode
	else:
		print("Invalid: -join flag missing")
		return -1, -1, -1, -1

def initiate_connection(host, port, username, passcode):
	
	def recieve_messages():
		while not connection_close:
			message = client_socket.recv(1024).decode()
			print(message)
			sys.stdout.flush()
			
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client_socket.connect((host, port))
	authentication_status = client_socket.recv(100).decode()
	
	if authentication_status == str(1):
		
		client_socket.send(passcode[:100].encode())
		auth_response = client_socket.recv(1024).decode()
		if auth_response.split(" ")[0] == "Incorrect":
			print(auth_response)
			sys.stdout.flush()
			client_socket.close()
			return
		else:
			print(auth_response)
			sys.stdout.flush()
			client_socket.send(username[:1024].encode())
			connection_close = False
			thread = threading.Thread(target=recieve_messages)
			thread.start()
			while True:
				msg = input()
				if msg == ":)":
					msg = "[feeling happy]"
				elif msg == ":(":
					msg = "[feeling sad]"
				elif msg == ":mytime":
					current_time = datetime.now()
					print(current_time.strftime("%a %b %d %H:%M:%S %Y"))
					sys.stdout.flush()
				elif msg == ":+1hr":
					current_time = datetime.now() + timedelta(hours=1)
					print(current_time.strftime("%a %b %d %H:%M:%S %Y"))
					sys.stdout.flush()
				client_socket.send(msg[:1024].encode())
				if msg == ":Exit":
					connection_close = True
					thread.join()
					client_socket.close()
					return

host, port, username, passcode = setup_parser()
if host != -1:
	initiate_connection(host, port, username, passcode)