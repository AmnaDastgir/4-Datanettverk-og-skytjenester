from socket import *
import sys
import select

#def main():
socketClient = socket(AF_INET, SOCK_STREAM) #Oppretter socket for client
clientPort = 1234 #setter port

    #koble til server
try:
    socketClient.connect(('127.0.0.1', clientPort))
except:
    print ("connection error")
    sys.exit()



while True:
    inputs = [sys.stdin, socketClient] 
    read_sockets,write_socket, error_socket = select.select(inputs,[],[]) 

    # we check if the message is either coming from your terminal or from a server
    for socks in read_sockets:
        if socks == socketClient:
            #lese data fra socket
            data = socketClient.recv(1024).decode()

            if (data == "exit" or not data):
                break
            #print
            print(data)

        else:
            #takes inputs from the user
            message = sys.stdin.readline()
             #sende data
            
            socketClient.send(message.encode());

    
socketClient.close()

