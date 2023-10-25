#                                                 TASK2

import sys
from socket import *
from email import message

#create a client socket object
socketClient = socket(AF_INET, SOCK_STREAM)
#get the IP adress and the port number from command line arguments
ipAdresse = (sys.argv[1]);
clientPort = int(sys.argv[2]);

#try to connect to the server
try:
    socketClient.connect((ipAdresse, clientPort))
except:
    print("Connection error")
    sys.exit()

#get the filename from the command line arguments
fileName = sys.argv[3]
#create the GET request
get = "GET /" + fileName + " HTTP/1.1"
print(get)

#send the GET request to the server
try:
    socketClient.send(get.encode())
except Exception as e:
    print("Error sending request: ", e)

#receive the data from the server
data = socketClient.recv(4096).decode('utf-8')
#print the data received
print(data.encode('utf-8'))
#close the socket
socketClient.close()