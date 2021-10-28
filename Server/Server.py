from socket import *
import time
from threading import Thread

HOST = '127.0.0.1'
# HOST = '192.168.31.15'
PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
users_dict = {}


def thread_for_client(conn, username):
    global users_dict
    connection = True
    recv_sock = socket(AF_INET, SOCK_STREAM)
    while connection:
        command = conn.recv(BUF_SIZE).decode()
        if command:
            com1 = command.split()[0]
            if com1 == 'LU':
                lu = ''
                for name in users_dict:
                    lu += '| {} |'.format(name)
                print('Sending LU for {}'.format(username))
                conn.send(lu.encode())
            elif com1 == 'DISCONNECT':
                conn.send('OK'.encode())
                conn.close()
                recv_sock.close()
                users_dict.pop(username)
                print('{} is disconnected'.format(username))
                break
            elif com1 == 'MESSAGE':
                mname = command.split()[1]
                if mname in users_dict.keys():
                    try:
                        recv_sock.connect((users_dict[mname], RECV_PORT))
                    except Exception as e:
                        print('Couldnt deliver message: ', e)
                        conn.send('Connection to receiving thread failed'.encode())
                        continue
                    msg = command.replace(mname, '')
                    recv_sock.send(msg.encode())
                    print('{} sent {} a message'.format(username, mname))
                else:
                    conn.send("{} is not online".format(command.split()[1]).encode())
            else:
                conn.send("Comm not added".encode())
        else:
            connection = False


s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
while True:
    print('Waiting for new connection')
    client_socket, client_address = s.accept()
    # print(clientsocket)
    name_check = client_socket.recv(BUF_SIZE).decode()
    username = name_check.split()[1]
    if username in users_dict:
        client_socket.send('ERROR'.encode())
        continue
    else:
        users_dict[username] = client_address[0]
        client_socket.send('OK'.encode())
        print('User {} connected to the server'.format(username))
    client_thread = Thread(target=thread_for_client, args=(client_socket, username), daemon=True)
    client_thread.start()

s.close()
