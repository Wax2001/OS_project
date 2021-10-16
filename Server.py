from socket import *

HOST = '127.0.0.1'
PORT = 8910
BUF_SIZE = 64

s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

while True:
    print('wait')
    try:
        clientsoclet, address = s.accept()
        name_check = clientsoclet.recv(BUF_SIZE).decode().split()[1]
        connection = False
        if name_check == 'sh':
            clientsoclet.send('Name is taken'.encode())
        else:
            clientsoclet.send(f'Welcome {name_check}'.encode())
            connection = True
            print('accepted')
        while connection:
            command = clientsoclet.recv(BUF_SIZE).decode()
            print(command)
            com1 = command.split()[0]
            if com1 == 'LU':
                clientsoclet.send("Server's LU".encode())
            elif com1 == 'QUIT' or com1 == 'DISCONNECT':
                break
            else:
                clientsoclet.send("Comm not added".encode())
            clientsoclet.close()
    except KeyboardInterrupt:
        print('\nServer closed')
        break
