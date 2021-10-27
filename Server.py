from socket import *
import time
from threading import Thread
HOST = '127.0.0.1'
# HOST = '192.168.31.15'
PORT = 2021
RECV_PORT = 2022
BUF_SIZE = 1024
users_list = []

def thread_for_client(conn, address, username):
    global users_list
    conn_recv = True
    connection = True
    recv_sock = socket(AF_INET, SOCK_STREAM)
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
        command = conn.recv(BUF_SIZE).decode()
        if command:
            print(command)
            com1 = command.split()[0]
            if com1 == 'LU':
                lu =''
                for tup in users_list:
                    lu += '| {} |'.format(tup[0])
                conn.send(lu.encode())
            elif com1 == 'DISCONNECT':
                conn.send('OK'.encode())
                conn.close()
                if not conn_recv:
                    recv_sock.close()
                users_list.remove((username, address[0]))
                break
            elif com1 == 'MESSAGE':
                print('Sending massage to {}'.format(command.split()[1]))
                if conn_recv:
                    try:
                        recv_sock.connect((address[0], RECV_PORT))
                        conn_recv = False
                    except Exception as e:
                        print('Couldnt deliver message: ', e)
                        conn.send('Connection to receiving thread failed'.encode())
                        continue
                msg = command.replace(command.split()[1], '')
                # print('connected to client receiver')
                recv_sock.send(msg.encode())
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
    if (username, client_address[0]) in users_list:
        client_socket.send('ERROR'.encode())
        continue
    else:
        users_list.append((username, client_address[0]))
        client_socket.send('OK'.encode())
        print('User {} connected to the server'.format(username))
    client_thread = Thread(target=thread_for_client, args=(client_socket, client_address, username), daemon=True)
    client_thread.start()


s.close()
