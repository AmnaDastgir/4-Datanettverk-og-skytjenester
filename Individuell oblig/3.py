#This code is a basic example of how to implement a server that can handle 
# multiple client requests simultaneously using threads.

#import the necessary
from socket import *
import socketserver
#important in order to terminate the program
import sys
import _thread as thread

#function to handle client request
def clientHandle(connection, addr):
    #while loop to receive and handle client message
    while True:
        #receive message from client and decode it
        message = connection.recv(2048).decode()
        #print the message received
        print(message)
        #extract the filename from the message
        fileName = message.split()[1]
        #open the file and read its content
        f = open(fileName [1:])
        outputdata = f.read();
        #send the file content back to the client
        connection.send(outputdata.encode())
    #close the connection
    connection.close()

#a main function to start the server
def main():
    #create a TCP socket for the server
    serverSocket = socket(AF_INET, SOCK_STREAM)
    #ask user to enter a port number to bind the server socket to
    serverPort = int(input("Select a port: "))
    #bind the server socket to the specified port number
    try:
        serverSocket.bind(('', serverPort))
    except:
        sys.exit
        print("Bind error: ")
    #listen for incoming client request
    serverSocket.listen(1)
    print("The server is currently ready to receive")

    #loop to accept client connection and spawn threads to handle them
    while True:
        try:
            #accept a client connection and get the client socket and address
            cSocket, addr = serverSocket.accept()
            #print the client address to the console
            print("The server socket is ready to serve", addr)
            #spawn a new thread to handle the client request 
            thread.start_new_thread(clientHandle, (cSocket, addr))
        except IOError:
            #send an error message to the client if the file is not found
            meld = "404 File not found"
            cSocket.send(meld.encode())

            #close the client socket
            cSocket.close()
        
        #close the server socket and exit the program
        serverSocket.close()
        sys.exit()
        
#call the main function to start the server        
main()