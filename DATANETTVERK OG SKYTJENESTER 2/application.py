from drtp import *
from config import *
import argparse
import socket
import sys
import time
import re
import os

###################################################
##################  SERVER SIDE ###################
###################################################


def server(server, port, file, protocol,
           payload_size=1024,
           window=1,
           timeout=0.5,
           loss_prob=0.001,
           max_skips=0,
           output=False):
    '''
    Description: This function implements the server side of the application.
    Parameters:
        server (str): server IP address
        port (int): server port
        file (str): file name (including path)
        protocol (str): protocol to be used (saw: Stop and Wait, gbn: Go Back N, sr: Selective Repeat)
        payload_size (int): size of the payload
        window (int): size of the window
        timeout (float): timeout value
        loss_prob (float): probability of packet loss
        max_skips (int): maximum number of skipped ACKs
        output (bool): output mode (True: verbose, False: quiet)
    '''
    # Bind to server
    sock = DRTPSocket()
    # Configure socket
    sock.config(payload_size, window, timeout, loss_prob, max_skips, output)

    try:
        sock.bind((server, port))
    except socket.error as e:
        print('Socket bind failed:', e)
        sys.exit()

    print('Server listening on', server, 'port', port, '...')
    sock.listen()  # Listen for incoming connections

    # Receive data
    print('Receiving data...')
    start = time.time()
    if protocol == 'saw':
        data = sock.recv('saw')
    if protocol == 'gbn':
        data = sock.recv('gbn')
    if protocol == 'sr':
        data = sock.recv('sr')
    end = time.time()

    # Write data to file
    with open(file, 'wb') as f:
        f.write(data)

    # Print statistics
    print('Received:', round(len(data) / 1000000, 2), 'MB')
    print('Time elapsed:', round(end - start, 2), 'seconds')
    print('Throughput:', round(len(data) / (end - start) / 1000000, 2), 'Mbps\n')


###################################################
##################  CLIENT SIDE ###################
###################################################

def client(server, port, file, protocol,
           payload_size=1024,
           window=1,
           timeout=0.5,
           loss_prob=0.001,
           max_skips=1,
           output=False):
    '''
    Description: This function implements the client side of the application.
    Parameters:
        server (str): server IP address
        port (int): server port
        file (str): file name (including path)
        protocol (str): protocol to be used (saw: Stop and Wait, gbn: Go Back N, sr: Selective Repeat)
        payload_size (int): size of the payload
        window (int): size of the window
        timeout (float): timeout value
        loss_prob (float): probability of packet loss
        max_skips (int): maximum number of skipped ACKs
        output (bool): output mode (True: verbose, False: quiet)
    '''
    # Connect to server
    sock = DRTPSocket()
    # Configure socket
    sock.config(payload_size, window, timeout, loss_prob, max_skips, output)

    # Connect to server
    if not sock.connect((server, port)):
        print('Socket connection failed. Try again later.')
        sys.exit()

    # Read file
    try:
        data = b''
        with open(file, 'rb') as f:
            data = f.read()
    except IOError as e:
        print('File not found:', e)
        sys.exit()

    # Send data to server
    print('Sending data...')
    if protocol == 'saw':
        sock.stop_and_wait(data)
    if protocol == 'gbn':
        sock.go_back_n(data)
    if protocol == 'sr':
        sock.selective_repeat(data)

    # Print statistics
    print('Sent:', round(len(data) / 1000000, 2), 'MB\n')


def parser():
    '''
    Description: This function parses the command line arguments and returns the mode of the application.
    Parameters: None
    Return:
        mode (str): mode of the application (server or client)
    '''
    # Create the parser
    parser = argparse.ArgumentParser(
        description="This is a simple file transfer application using the DRTP protocol.")

    # Add arguments to the parser
    parser.add_argument('-s', '--server', action='store_true',
                        help='enable the server mode')
    parser.add_argument('-c', '--client', action='store_true',
                        help='enable client mode')
    parser.add_argument('-b', '--server_ip', default=SERVER,
                        help='IP address of the server')
    parser.add_argument('-p', '--server_port', default=PORT,
                        help='Port number of the server')
    parser.add_argument('-f', '--file', default=None,
                        help='Path to the file')
    parser.add_argument('-m', '--mode', default=None,
                        help='Reliability function to be used: stop-and-wait, go-back-n, selective-repeat')
    parser.add_argument('-r', '--reliability', default=None,
                        help='Reliability function to be used: stop-and-wait, go-back-n, selective-repeat')
    parser.add_argument('-t', '--test', default=None,
                        help='Test to be run: skipack (server-side), loss (client-side)')
    parser.add_argument('-o', '--output', action='store_true',
                        help='Print details of the packets sent and received')

    args = parser.parse_args()  # parse the command line arguments

    # Handle errors in the command line arguments

    if (args.server == False and args.client == False) or (args.server == True and args.client == True):
        print("Error: you must run either in server or client mode")
        sys.exit(1)

    # Check the mode of test
    test = False
    if args.test:
        if args.test not in ["loss", "skipack"]:
            print("Error: invalid option for test")
            sys.exit(1)
        test = True

    # If -s flag is specified, flag -r is not allowed
    if args.server:
        if args.mode is None:
            args.mode = PROTOCOL
        if args.reliability is not None:
            print("Error: invalid flag -r for server mode")
            sys.exit(1)
        if args.test == 'loss':
            print("Error: invalid option for test")
            sys.exit(1)

    # If -c flag is specified, flag -m is not allowed
    if args.client:
        if args.reliability is None:
            args.reliability = PROTOCOL
        if args.mode is not None:
            print("Error: invalid flag -m for client mode")
            sys.exit(1)
        if args.test == 'skipack':
            print("Error: invalid option for test")
            sys.exit(1)

    # Check if the IP address is valid
    pattern_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    match = re.match(pattern_ip, args.server_ip)
    if match == None:
        print("Error: invalid IP address")
        sys.exit(1)

    try:
        socket.inet_aton(args.server_ip)
    except socket.error:
        print("Error: invalid IP address")
        sys.exit(1)

    # Check if the port number is valid
    try:
        args.server_port = int(args.server_port)
    except ValueError:
        print("Error: port number must be an integer")
        sys.exit(1)

    if args.server_port < 1024 or args.server_port > 65535:
        print("Error: port number must be between 1024 and 65535")
        sys.exit(1)

    # Check if the operation mode or reliability function is valid
    if args.server and args.mode not in ["saw", "gbn", "sr"]:
        print("Error: invalid operation mode")
        sys.exit(1)
    if args.client and args.reliability not in ["saw", "gbn", "sr"]:
        print("Error: invalid reliability function")
        sys.exit(1)

    # Check if the file exists when the client mode is enabled
    if args.file:
        if args.client == True:
            if not os.path.isfile(args.file):
                print("Error: file does not exist")
                sys.exit(1)
    else:
        print("Error: you must specify the path to the file")
        sys.exit(1)

    output = False
    if args.output:
        output = True

    # Call the server or client function based on the command line arguments:
    if args.server:
        server(server=args.server_ip,
               port=args.server_port,
               file=args.file,
               protocol=args.mode,
               payload_size=PAYLOAD_SIZE,
               window=WINDOW,
               timeout=TIMEOUT,
               loss_prob=LOSS_PROB,
               max_skips=MAX_SKIP_ACKS if test else 0,
               output=output)

    elif args.client:
        client(server=args.server_ip,
               port=args.server_port,
               file=args.file,
               protocol=args.reliability,
               payload_size=PAYLOAD_SIZE,
               window=WINDOW,
               timeout=TIMEOUT,
               loss_prob=LOSS_PROB,
               max_skips=MAX_LOSS_PACKETS if test else 0,
               output=output)

    else:
        sys.exit(1)


if __name__ == "__main__":
    parser()
