import subprocess
import argparse
import socket
import sys
import time
import re
import threading

# Global variables
default_server = '127.0.0.1'
default_port = 8088
default_time = 25
default_format = 'MB'
default_interval = 1
default_parallel = 1
default_num_bytes = '0B'


def format_bytes(num_bytes, format):
    '''
    Description: This function is used to convert bytes to KB or MB
    Parameters:
        num_bytes: number of bytes to be converted
        format: format of the summary of the results – it should be either in B, KB or MB, default=MB
    Returns:
        num_bytes: number of bytes converted to KB or MB
    '''
    if format == 'KB':
        return num_bytes / 1000
    elif format == 'MB':
        return num_bytes / 1000000
    else:
        return num_bytes


def tabs(data, format):
    '''
    Description: This function is used to add tabs to the output and align the results
    Parameters:
        data: data to be printed
        format: format of the summary of the results
    Returns:
        tabs: tabs to be added to the output
    '''
    if len(f"{data:.0f}" + format) < 7:
        return "\t\t"
    else:
        return "\t"

###################################################
##################  SERVER SIDE ###################
###################################################


def server(server, port, format):
    '''
    Description: This function creates a server socket and listens for incoming connections.
    It then creates a thread for each client that connects to the server.
    Parameters:
        server: The IP address of the server's interface where the client should connect
        port: The port number on which the server should listen
        format: The format of the summary of results - it should be either in B, KB or MB
    Returns:
        None
    '''
    server_socket = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
    try:
        # bind the socket to the server and port
        server_socket.bind((server, port))
    except socket.error as e:
        print("Socket binding error: ", str(e))
        sys.exit()

    server_socket.listen(5)  # listen for incoming connections

    print("-" * 45)
    print("A simpleperf server is listening on port {}".format(port))
    print("-" * 45 + "\n")

    while True:
        try:
            parallel = 5  # maximum number of parallel connections is 5
            threads = []
            summary = []

            i = 0
            while i < parallel:
                conn, addr = server_socket.accept()  # accept incoming connection
                # receive the number of parallel connections from the client
                parallel = int(conn.recv(1).decode('utf-8'))

                print("A simpleperf client with {}:{} is connected with {}:{}".format(
                    addr[0], addr[1], server, port))

                t = threading.Thread(target=handle_server, args=(
                    conn, addr, format, summary, i))  # create a thread for each client
                threads.append(t)
                t.start()

                i += 1

            # Wait for all threads to finish
            for t in threads:
                t.join()  #huske å fjerne

            # Print the summary of each connection
            print("\nID\t\tInterval\tReceived\tRate\n")
            for i in range(parallel):
                print(summary[i])
            print()
            threads.clear()
            summary.clear()   
            
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            server_socket.close()
            break
    
    sys.exit()

def handle_server(conn, addr, format, summary, i):
    '''
    Description: This function handles the server side of the connection.
    It receives data from the client and calculates the time elapsed, total bytes received,
    and the rate at which traffic could be read in megabits per second (Mbps).
    Parameters:
        conn: The socket object for the connection
        addr: The address of the client. It is a tuple of (ip
        format: The format of the summary of results - it should be either in B, KB or MB
        event: Event object used to synchronize threads
        summary: list of summary results for each connection
        i: index of the connection
    Returns:
        None
    '''

    # Receive data from client
    total_bytes = 0
    start_time = time.time()
    while True:
        data = conn.recv(1000)
        if data.endswith(b"BYE"):
            break
        total_bytes += len(data)
    end_time = time.time()

    # Receive BYE message from client and send acknowledgement to client
    conn.sendall("ACK: BYE".encode())
    conn.close()

    # Calculate the time elapsed in seconds
    time_elapsed = end_time - start_time

    # Calculate rate in Mbps
    if time_elapsed == 0:
        rate = 0
    else:
        rate = (total_bytes * 8) / time_elapsed / 1000000

    # Format total_bytes in the desired format
    received = format_bytes(total_bytes, format)

    # Print results
    (ip_client, port) = addr
    ntabs = tabs(received, format)
    result = f"{ip_client}:{port}\t0.0 - {time_elapsed:.1f}\t{received:.0f} {format}{ntabs}{rate:.2f} Mbps"
    summary.append(result)


###################################################
##################  CLIENT SIDE ###################
###################################################

def client(server, port, time_, format, interval, parallel, num_bytes):
    '''
    Description: This function creates a client socket and the parallel connections to the server.
    Parameters:
        server: IP address of the server
        port: port number of the server
        time_: the total duration in seconds for which data should be generated, also sent to the server (if it is set with -t flag at the client side) and must be > 0. If do not use -t flag, client runs for 25 seconds
        format: format of the summary of the results – it should be either in B, KB or MB, default=MB
        interval: prints statistics per z second
        parallel: creates parallel connections to connect to the server and send data – it must be 1 and max value should be 5 – default: 1
        num_bytes: transfer number of bytes specified by -n flag, it should be either in B, KB or MB. If -n flag is not specified, client will send data for 25 seconds
    Returns:
        None
    '''

    threads = []
    summary = []
    # Create a thread for each connection
    for i in range(parallel):
        # Create a new socket for each connection for different ports
        client_socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)  # create a TCP socket
        client_socket.settimeout(5)  # set a timeout of 5 seconds

        try:
            client_socket.connect((server, port))  # connect to the server
            client_socket.send(str(parallel).encode())

        except socket.error as e:
            print("Error connecting to server: ", e)
            client_socket.close()
            sys.exit(1)

        # Print the main header
        if i == 0:
            print("-" * 64)
            print("A simpleperf client connecting to server {}, port {}".format(
                server, port))
            print("-" * 64 + "\n")

        # Create a thread for each connection
        t = threading.Thread(target=handle_client, args=(
            client_socket, server, port, time_, format, interval, parallel, num_bytes, summary))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Print the summary of each connection
    if parallel > 1:
        print("\nID\t\tInterval\tTransfer\tBandwidth\n")

    for i in range(parallel):
        print(summary[i])
    print()


def handle_client(client_socket, server, port, time_, format, interval, parallel, num_bytes, summary):
    '''
    Description: This function handles the client side of the connection.
    Parameters:
        client_socket: client socket to connect to the server
        server: IP address of the server
        port: port number of the server
        time_: the total duration in seconds for which data should be generated, also sent to the server (if it is set with -t flag at the client side) and must be > 0. If do not use -t flag, client runs for 25 seconds
        format: format of the summary of the results – it should be either in B, KB or MB, default=MB
        interval: prints statistics per z second
        parallel: creates parallel connections to connect to the server and send data – it must be 1 and max value should be 5 – default: 1
        num_bytes: transfer number of bytes specified by -n flag, it should be either in B, KB or MB. If -n flag is not specified, client will send data for 25 seconds
        summary: list of summary results for each connection
    Returns:
        None
    '''
    # Get the client ip and port
    (client_ip, client_port) = client_socket.getsockname()

    print("Client ip {}:{} connected with server {} port {}".format(
        client_ip, client_port, server, port))

    # Convert num_bytes to an integer
    if num_bytes[-1] == "B" and num_bytes[-2] not in ["K", "M"]:
        num_bytes = int(num_bytes[:-1])
    elif num_bytes[-2:] == "KB":
        num_bytes = int(num_bytes[:-2]) * 1000
    elif num_bytes[-2:] == "MB":
        num_bytes = int(num_bytes[:-2]) * 1000000

    total_data = 0
    start_time = time.time()

    # If -n flag is specified, send data for the specified number of bytes
    if num_bytes != 0:
        while total_data < num_bytes:
            data = b"0" * 1000
            client_socket.send(data)
            total_data += len(data)

    if parallel == 1:
        print("\nID\t\tInterval\tTransfer\tBandwidth\n")

    # If -n flag is not specified, send data for 25 seconds or the specified time and print the results in the specified interval
    if num_bytes == 0:
        interval_data = 0
        interval_start_time = start_time

        while interval_start_time - start_time < time_:
            data = b"0" * 1000
            client_socket.send(data)
            total_data += len(data)
            interval_data += len(data)
            current_time = time.time()

            # If the specified interval has elapsed or the specified time has elapsed, print the results
            if (current_time - interval_start_time >= interval or current_time - start_time >= time_):

                if parallel == 1:
                    # Calculate the bandwidth
                    bandwidth = (interval_data * 8) / (interval * 1000000)
                    # Format the total data to the specified format
                    total_sent_data = format_bytes(interval_data, format)
                    # Print statistics for the current interval
                    ntabs = tabs(total_sent_data, format)
                    print(f"{client_ip}:{client_port}\t{interval_start_time - start_time:.1f} - {current_time - start_time:.1f}\t{total_sent_data:.0f} {format}{ntabs}{bandwidth:.2f} Mbps")

                # Reset the interval data and start time
                interval_data = 0
                interval_start_time = time.time()

    # Send message to the server and wait for the acknowledgement message
    client_socket.sendall(b"BYE")
    client_socket.recv(1024)
    client_socket.close()

    # Calculate the total time elapsed
    end_time = time.time()
    time_elapsed = end_time - start_time

    # Calculate the bandwidth
    if time_elapsed == 0:
        bandwidth = 0
    else:
        bandwidth = (total_data * 8) / (time_elapsed * 1000000)

    # Format the total data to the specified format
    total_sent_data = format_bytes(total_data, format)

    # Print the summary of the results
    ntabs = tabs(total_sent_data, format)
    if parallel == 1 and num_bytes == 0:
        print("\n" + "-" * (61 + len(f"{bandwidth:.2f}")) + "\n")

    result = f"{client_ip}:{client_port}\t{start_time - start_time:.1f} - {end_time - start_time:.1f}\t{total_sent_data:.0f} {format}{ntabs}{bandwidth:.2f} Mbps"
    summary.append(result)


###################################################
################ PARSE ARGUMENTS ##################
###################################################

def mode():
    '''
    Description: This function parses the command line arguments and returns the mode of the application.
    Parameters:
        None
    Returns:
        None
    '''
    # Create the parser
    parser = argparse.ArgumentParser(
        description="A simpleperf client/server application")

    # Add arguments to the parser
    parser.add_argument('-s', '--server', action='store_true',
                        help='enable the server mode')
    parser.add_argument('-c', '--client', action='store_true',
                        help='enable client mode')
    parser.add_argument('-b', '--bind', default=default_server,
                        help='IP address of the server')
    parser.add_argument('-I', '--serverip', default=default_server,
                        help='IP address of the server')
    parser.add_argument('-p', '--port', default=default_port,
                        help='Port number of the server')
    parser.add_argument('-f', '--format', default=default_format,
                        help='Format of the summary of results (B, KB or MB)')
    parser.add_argument('-t', '--time', default=default_time,
                        help='Time in seconds for which data should be generated')
    parser.add_argument('-n', '--num_bytes', default=default_num_bytes,
                        help='Number of bytes to be sent')
    parser.add_argument('-P', '--num_conn', default=default_parallel,
                        help='Number of parallel connections')
    parser.add_argument('-i', '--interval', default=default_interval,
                        help='Interval in seconds for which the results should be printed')
    

    args = parser.parse_args()  # parse the command line arguments

    # Handle errors in the command line arguments

    if (args.server == False and args.client == False) or (args.server == True and args.client == True):
        print("Error: you must run either in server or client mode")
        sys.exit(1)

    # If -s flag is specified, only allow the -b, -p and -f flags
    if args.server == True:
        if args.serverip != default_server or args.time != default_time or args.num_bytes != default_num_bytes or args.num_conn != default_parallel or args.interval != default_interval:
            print("Error: invalid flags for server mode")
            sys.exit(1)
        

    # If -c flag is specified, only allow the -I, -p, -t, -f, -i, -P and -n flags
    if args.client == True:
        if args.bind != default_server:
            print("Error: invalid flags for client mode")
            sys.exit(1)

    pattern_ip = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    match = re.match(pattern_ip, args.bind) and \
        re.match(pattern_ip, args.serverip)
    if match == None:
        print("Error: invalid IP address")
        sys.exit(1)

    try:
        socket.inet_aton(args.bind) and socket.inet_aton(args.serverip)
    except socket.error:
        print("Error: invalid IP address")
        sys.exit(1)

    try:
        args.port = int(args.port)
    except ValueError:
        print("Error: port number must be an integer")
        sys.exit(1)

    if args.port < 1024 or args.port > 65535:
        print("Error: port number must be between 1024 and 65535")
        sys.exit(1)

    if args.format not in ["B", "KB", "MB"]:
        print("Error: invalid format specified")
        sys.exit(1)

    try:
        args.time = int(args.time)
    except ValueError:
        print("Error: time must be an integer")
        sys.exit(1)

    if args.time <= 0:
        print("Error: time must be greater than 0")
        sys.exit(1)

    pattern_bytes = r'^\d+[K|M]?B$'
    # check if the number of bytes
    match = re.match(pattern_bytes, args.num_bytes)
    if match == None:
        print("Error: invalid number of bytes")
        sys.exit(1)

    try:
        args.num_conn = int(args.num_conn)
    except ValueError:
        print("Error: number of parallel connections must be an integer")
        sys.exit(1)

    if args.num_conn < 1 or args.num_conn > 5:
        print("Error: number of parallel connections must be between 1 and 5")
        sys.exit(1)

    try:
        args.interval = int(args.interval)
    except ValueError:
        print("Error: interval must be an integer")
        sys.exit(1)

    if args.interval <= 0:
        print("Error: interval must be greater than 0")
        sys.exit(1)

    # Call the server or client function based on the command line arguments
    if args.server:
        server(args.bind, args.port, args.format)
    elif args.client:
        client(args.serverip, args.port, args.time, args.format,
               args.interval, args.num_conn, args.num_bytes)
    else:
        sys.exit(1)

if __name__ == "__main__":
    mode()
