# lage en webserver som håndterer en HTTP request om gangen, webserveres skal akseptere og "parse" HTTP-requesten,
# hente den forespurte fila fra serverens filsystem, lage en HTTP response melding som inneholder
# requested filen "preceded in the server", også sende svar direkte til klienten, 
#hvis svarmeldingen ikke finnes skal man sende feilmelding om dette

#                                                 TASK1

from socket import *                                                    #import socket module
import sys                                                              #import the sys module to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM)                             #In order to terminate the program, create a socket object

port = int(input("Select port : "))                                     #get the port number from the user
serverSocket.bind(('', port))                                           #get the port number from the user
serverSocket.listen(1)                                                  #Send one HTTP header line into socket
print("The server is ready to receive")                                 #print a message to confirm that the server is ready to receive

while True:                                                             #start an infinite loop to keep the server running
    #connectionSocket, addr = serverSocket.accept()                     #Establish the connection print('Ready to serve...') connectionSocket, addr =
    try:
        connectionSocket, addr = serverSocket.accept()                  #Establish the connection print('Ready to serve...') connectionSocket, addr =
        print("server is ready to serve", addr)                         #print a message to confirm that the connection is establish
        message = connectionSocket.recv(1024).decode()                  #receive the HTTP request from the client
        filename = message.split()[1]                                   #parse the message to get the requested file name
        f = open(filename[1:])                                          #open the requested file and read its content
        outputdata = f.read() 
        lengde = len(outputdata)
        print(outputdata)
        #f.close()
        
        '''
        header = 'HTTP/1.1 200 OK\n'                                    #construct the HTTP response header
        header += 'Connection:close\n'
        header += 'Content-Length: ' + str(lengde)
        header += '\nContent-Type: text/html\n\n'
        connectionSocket.send(header.encode())
        '''
        header = "HTTP/1.1 200 OK\nConnection:close\nContent-type:text/html\nContent-length:"
        header += str(lengde) + "\n\n"
        connectionSocket.send(header.encode())
        
        connectionSocket.send(outputdata.encode())       
        connectionSocket.close()
    except IOError:
        response = 'HTTP/1.1 404 Not Found\r\n\r\n'                     #Send response message for file not found
        connectionSocket.send(response.encode())                        
        connectionSocket.close()                                        #Close client socket


serverSocket.close()                                                    # Terminate the program after sending the corresponding data
sys.exit()
