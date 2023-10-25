#                                                 TASK2

#import socket module
from socket import *
#import the sys module to terminate the program
import sys
import socketserver

#In order to terminate the program, create a socket object
serverSocket = socket(AF_INET, SOCK_STREAM) 
#prompt the user to enter a port number to bind the socket
serverPort = int(input("Select a port:"))

#bind the server to the portnumber
if serverSocket.bind('', serverPort):
    print("Vellykket binding")
else:
    sys.exit()
    print("Bind failed. ")

#listen for incoming connections
serverSocket.listen(1)
#print a message to indicate that the server is ready
print("Server is ready")

#while loop to handle incoming connections                                                                 
while True:
    #accept a connection                                                                              
    try:
        cSocket, addr = serverSocket.accept()
        #print a message to indicate that the server is ready to serve
        print("Server is ready to serve ", addr)
        #receive the HTTP request message from the client
        message = cSocket.recv(2048).decode()
        #print the message
        print(message)
        #get the file name from the message
        fileName = message.split()[1]
        #open the file
        f = open(fileName [1:])
        #read the content of the file
        outputdata = f.read();
        #print the output data
        print("Output data \n\n"+outputdata+"\n\n")
        #get the length of the output data
        lengde = len(outputdata)
        #send the output data to the cliend
        cSocket.send(outputdata.encode())
        #close the client socket
        cSocket.close()

    #handle the case when the requested file is not found
    except IOError:
        #send an error message to the client
        melding = "404 File mot found"
        cSocket.send(melding.encode())
        #close the client socket
        cSocket.close()


        #connectionSocket, addr = serverSocket.accept()                  
        #print("server is ready to serve", addr)                         
        #message = connectionSocket.recv(1024).decode()               
        #filename = message.split()[1]                               
        #f = open(filename[1:])                                          
        #outputdata = f.read()
        #f.close() 
        #lengde = len(outputdata)
        #print(outputdata)    
        #connectionSocket.send(header.encode())
        
        #connectionSocket.send(outputdata.encode())       
        #connectionSocket.close()
    #except IOError:
        #response = 'HTTP/1.1 404 Not Found\r\n\r\n'                
        #connectionSocket.send(response.encode())                        
        #connectionSocket.close()                                

#close the server socket and terminate the program
serverSocket.close() 
sys.exit()