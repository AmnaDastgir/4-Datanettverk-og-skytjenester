# DRTP PROTOCOL

## Overview

The **DATA2410 Reliable Transport Protocol (DRTP)** is a simple transport protocol that provides reliable data delivery on top of UDP. This protocol ensures that data is reliably delivered in-order without missing data or duplicates. A simple transfer application is implemented on top of the **DRTP** protocol to demonstrate its functionality. It is a client-server application that allows a client to send a file to a server. The protocol and the application have been implemented in Python and tested in a Mininet environment.

## Prerequisites

Make sure you have the Python interpreter installed on your system before getting started:

-   python3 (verify with `python3 --version`)

The next tools are required to run the client-server application in a Mininet environment:

-   mininet (verify with `sudo mn --version`)
-   xterm (verify with `xterm -version`)

## Installation

If you don't have any of the dependencies installed, you can install them by running the following commands in the terminal:

```
$ sudo apt install python3-pip
$ pip install mininet
$ sudo apt-get install mininet
$ sudo apt-get install xterm
```

To run the program, first make sure the necessary ports are available. You can do this by running the following commands:

```
$ sudo mn -c
$ sudo fuser -k 6653/tcp
```

## Server mode

When you run the application in server mode, server will receive a file from a client through its **DRTP/UDP** socket and write it to the file system. The file name and the port numbers on which the server listens are given as command line arguments.

To run the application in server mode with the default options, it must be invoked as follows:

```
$ python3 application -s -f Photo.jpg
```

Where `-s` indicates the application is running in a server mode and `-f` specifies the file to be received from the client.

The server prints the following and wait for a connection:

```
Server listening on <IP> port XXXX
```

If you want to specify the operation mode used by the **DRTP** protocol, for example Go-Back-N (gbn), then run the next command:

```
$ python3 application.py -s -f file -m gbn
```

If you want to skip an ack to trigger retransmission at the sender-side, then run the next command:

```
$ python3 application.py -s -f file -m gbn -t skippack
```

When a client connects and sends a file, the server prints the following while receiving the file:

```
Connected to (<IP>, XXXX)
Receiving data...
```

If you want to see the acks packets sent by the server, then use the -o option:

```
$ python3 application.py -s -f file -m gbn -t skippack -o
```

This will print the acks sent by the server:

```
Server listening on <IP> port XXXX
ack_num 1 seq_num 1, flags: ACK 1, SYN 1, FIN 0, RST 0, Data sent: 0
Connected to (<IP>, XXXX)
Receiving data...
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: 0
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: 0
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: 0
...
All packets received
ack_num X seq_num X, flags: ACK 1, SYN 0, FIN 1, RST 0, Data sent: 0
Connection closed
```

The printed line for each packet has information about the ack number, sequence number, flags, and the data sent. The flags are represented as follows: ACK, SYN, FIN, RST. The ack number and sequence number are represented in decimal. The flags are represented in binary. The data sent is the number of bytes sent in the packet and it is represented in decimal.

At the end of the transfer, server prints total number of bytes received, the total time taken to receive the file and the throughput of the transfer:

```
Number of ack lost: X
Received: X MB
Time elapsed: X seconds
Throughput: X Mbps
```

## Client mode

When you run the application in client mode, client will send a file to a server through its **DRTP/UDP** socket. The server name, port number and file name are given as command line arguments. Client mode sends data in chunks of 1460 bytes by default. Sender initiates a three-way handshake with the receiver (similar to TCP) to establish a reliable connection before sending the data.

To run the application in client mode with the default options, it must be invoked as follows:

```
$ python3 application -c -f Photo.jpg
```

Where `-c` indicates the application is running in a client mode and `-f` specifies the file to be sent to the server.

If you want to specify the reliability algorithm used by the **DRTP** protocol, for example Go-Back-N (gbn), then run the next command:

```
$ python3 application.py -c -f file -r gbn
```

If you want to test duplicate/reordering/packet-loss scenario, then run the next command (use the -o option to see the acks packets sent):

```
$ python3 application.py -c -f file -r gbn -t loss -o
```

This will print the packets sent by the client:

```
ack_num 0 seq_num 1, flags: ACK 0, SYN 1, FIN 0, RST 0, Data sent: 0
ack_num 1 seq_num 1, flags: ACK 1, SYN 0, FIN 0, RST 0, Data sent: 0
Connected to (<IP>, XXXX)
Sending data...
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: X
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: X
ack_num X seq_num X, flags: ACK X, SYN X, FIN 0, RST 0, Data sent: X
...
All packets sent
ack_num X seq_num X, flags: ACK 0, SYN 0, FIN 1, RST 0, Data sent: X
Connection closed
```

At the end of the transfer, client prints the number of packets lost and the total number of bytes sent:

```
Number of packets lost: X
Sent: X MB
```

## Available options

Table below lists all the available options that you can use in server/client mode.

| <div style="width: 50px">**Flag**</div> | <div style="width: 110px">**Long flag**</div> | <div style="width: 110px">**Input**</div> | <div style="width: 50px">**Type**</div> | <div style="width: 100px">**Description**</div>                                                                                                                   |
| --------------------------------------- | --------------------------------------------- | ----------------------------------------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `-s`                                    | `--server`                                    | **X**                                     | boolean                                 | enables the server mode.                                                                                                                                          |
| `-c`                                    | `--client`                                    | **X**                                     | boolean                                 | enables the client mode.                                                                                                                                          |
| `-b`                                    | `--server_ip`                                 | **ip address**                            | string                                  | allows to select the **ip address** of the server's interface where the client should connect. _Default_: `127.0.0.1`                                             |
| `-p`                                    | `--server_port`                               | **port number**                           | integer                                 | allows to use select **port number** on which the server should listen; the port must be an integer and in the range [1024, 65535]. _Default_: `8088`             |
| `-f`                                    | `--file`                                      | **file**                                  | string                                  | allows to select the **file** to be sent to the server.                                                                                                           |
| `-m`                                    | `--mode`                                      | **mode**                                  | string                                  | allows to select the operation **mode** used by DRTP protocol (server mode): saw (Stop and Wait), gbn (Go-Back-N), sr (Selective Repeat). _Default_: `saw`        |
| `-r`                                    | `--reliability`                               | **reliability**                           | string                                  | allows to select the **reliability** algorithm used by DRTP protocol (client mode): saw (Stop and Wait), gbn (Go-Back-N), sr (Selective Repeat). _Default_: `saw` |
| `-t`                                    | `--test`                                      | **test mode**                             | string                                  | allows to select the **test mode**: loss (client mode), skipack (server mode).                                                                                    |
| `-o`                                    | `--output`                                    | **X**                                     | string                                  | allows to print the output of the packet transfer process.                                                                                                        |

You can also change the default parameter values used in the application by editing the `config.py` file. The default values are listed below:

```
SERVER = '127.0.0.1'
PORT = 8088
PROTOCOL = 'saw'  # default: stop and wait
PAYLOAD_SIZE = 1460
WINDOW = 5
TIMEOUT = 0.5
MAX_LOSS_PACKETS = 5
MAX_SKIP_ACKS = 5
LOSS_PROB = 0.001  # 0.1%
```

Here is a brief description of each parameter:

| <div style="width: 80px">**Parameter**</div> | <div style="width: 100px">**Description**</div>                                                                                   |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `SERVER`                                     | **ip address** of the server's interface where the client should connect. _Default_: `127.0.0.1`                                  |
| `PORT`                                       | **port number** on which the server should listen; the port must be an integer and in the range [1024, 65535]. _Default_: `8088`  |
| `PROTOCOL`                                   | reliability function used by the **DRTP** protocol: saw (Stop and Wait), gbn (Go-Back-N), sr (Selective Repeat). _Default_: `saw` |
| `PAYLOAD_SIZE`                               | **payload size** of the packets sent by the client. _Default_: `1460`                                                             |
| `WINDOW`                                     | **window size** of the packets sent by the client. _Default_: `5`                                                                 |
| `TIMEOUT`                                    | **timeout** time in second used by the client to wait for an ack packet. _Default_: `0.5`                                         |
| `MAX_LOSS_PACKETS`                           | **max number** of packets lost during the transfer (for test purposes). _Default_: `5`                                            |
| `MAX_SKIP_ACKS`                              | **max number** of ack packets skipped during the transfer (for test purposes). _Default_: `5`                                     |
| `LOSS_PROB`                                  | **probability** of packet loss during the transfer (for test purposes). _Default_: `0.001`                                        |

## Execution examples

<img width="900" title="screenshot_01" alt="screenshot_01" src="./img/img_01.jpg">

<img width="900" title="screenshot_02" alt="screenshot_02" src="./img/img_02.jpg">

<img width="900" title="screenshot_03" alt="screenshot_03" src="./img/img_03.jpg">

<img width="900" title="screenshot_04" alt="screenshot_04" src="./img/img_04.jpg">

<img width="900" title="screenshot_05" alt="screenshot_05" src="./img/img_05.jpg">

