from socket import *
import time

HOST = '127.0.0.1'
# HOST = '192.168.31.15'
PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
con_recv = True

s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
while True:
    print('wait')
    clientsocket, address = s.accept()
    print(clientsocket)
    name_check = clientsocket.recv(BUF_SIZE).decode().split()[1]
    # if name_check:
    #     print(name_check, '/', address[0], '/', type(address[0]))
    # else:
    #     print('ffq')
    clientsocket.send('OK'.encode())

    recv_sock = socket(AF_INET, SOCK_STREAM)

    connection = True
    while connection:
        # try:
        #     print((address[0], RECV_PORT))
        #     time.sleep(1)
        #     recv_sock.connect((address[0], RECV_PORT))
        #     print('connected to client receiver')
        #     recv_sock.send('hi recv sock'.encode())
        #
        # except Exception as e:
        #     print(f'Connection to Clients recv socket is failed {e} ')
        #     break
        command = clientsocket.recv(BUF_SIZE).decode()
        if command:
            print(command)
            com1 = command.split()[0]
            if com1 == 'LU':
                clientsocket.send("Server's LU".encode())
            elif com1 == 'DISCONNECT' or com1 == "QUIT":
                clientsocket.send('OK'.encode())
                clientsocket.close()
                recv_sock.close()
                con_recv = True
                break
            elif com1 == 'MESSAGE':
                print('Sending massage to {}'.format(command.split()[1]))
                if con_recv:
                    recv_sock.connect((address[0], RECV_PORT))
                    con_recv = False
                msg = command.replace(command.split()[1], '')
                # print('connected to client receiver')
                recv_sock.send(msg.encode())
            else:
                clientsocket.send("Comm not added".encode())
        else:
            connection = False

s.close()
