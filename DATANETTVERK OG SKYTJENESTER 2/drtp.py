import socket
import struct
import random
import time


class DRTPHeader:
    '''
    Description: This class implements the DRTP header. It is used to pack and unpack the header.
    Methods:
        pack(): packs the header into a byte string
        unpack(): unpacks the header from a byte string
    '''

    def __init__(self, seq_num, ack_num, syn_flag=0, ack_flag=0, fin_flag=0, reset_flag=0, window=64):
        self.seq_num = seq_num  # sequence number
        self.ack_num = ack_num  # ack number
        self.syn_flag = syn_flag  # SYN flag
        self.ack_flag = ack_flag  # ACK flag
        self.fin_flag = fin_flag  # FIN flag
        self.reset_flag = reset_flag  # RST flag
        self.window = window  # window size

    def pack(self):
        '''
        Description: Packs the header into a byte string.
        Parameters: None
        Return: Byte string
        '''
        flags = (self.syn_flag << 3) + (self.ack_flag << 2) + \
            (self.fin_flag << 1) + (self.reset_flag)
        return struct.pack('!IIHH', self.seq_num, self.ack_num, flags, self.window)

    @classmethod
    def unpack(cls, data):
        '''
        Description: Unpacks the header from a byte string.
        Parameters: Byte string
        Return: DRTPHeader object
        '''
        seq_num, ack_num, flags, window = struct.unpack('!IIHH', data)
        syn_flag = (flags & 0b1000) >> 3
        ack_flag = (flags & 0b0100) >> 2
        fin_flag = (flags & 0b0010) >> 1
        reset_flag = flags & 0b0001
        return cls(seq_num, ack_num, syn_flag, ack_flag, fin_flag, reset_flag, window)


class DRTPPacket:
    '''
    Description: This class implements the DRTP packet. It is used to pack and unpack the packet.
    Methods:
        pack(): packs the packet into a byte string
        unpack(): unpacks the packet from a byte string
    '''

    def __init__(self, header, payload=b''):
        self.header = header
        self.payload = payload

    def pack(self):
        '''
        Description: Packs the packet into a byte string.
        Parameters: None
        Return: Byte string
        '''
        return self.header.pack() + self.payload

    @classmethod
    def unpack(cls, data):
        '''
        Description: Unpacks the packet from a byte string.
        Parameters: Byte string
        Return: DRTPPacket object
        '''
        header = DRTPHeader.unpack(data[:12])
        payload = data[12:]
        return cls(header, payload)

    def __str__(self):
        return f'{self.header.seq_num}, {self.header.ack_num}, {self.header.flags}, {self.data}'


class DRTPSocket:
    '''
    Description: This class implements the DRTP socket. It is used to send and receive packets.
    Methods:
        bind(): binds the socket to the given address
        config(): configures the socket with the given parameters
        send(): sends a packet with the given payload and flags to the destination address
        connect(): connects the socket to the destination address
        listen(): listens for connections
        close(): closes the socket
        stop_and_wait(): Stop and Wait protocol
        go_back_n(): Go Back N protocol
        selective_repeat(): Selective Repeat protocol
        recv(): receives a packet from the source address
    '''

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = None
        self.size = 1000  # max payload size
        self.seq_num = 0  # next seq_num to send
        self.ack_num = 0  # next expected seq_num or ack_num
        self.send_buffer = {}  # key: seq_num, value: packet
        self.recv_buffer = {}  # key: seq_num, value: data
        self.window_size = 64
        self.timeout = 0.5
        self.loss_prob = 0.001  # 0.1% chance of packet loss or ack loss
        self.max_skips = 0
        self.num_skips = 0
        self.output = False

    def bind(self, addr):
        '''
        Description: Binds the socket to the given address.
        Parameters: 
            addr (tuple): the address to bind to
        Return: None
        '''
        self.sock.bind(addr)

    def config(self, payload_size=1000, window=64, timeout=0.5, loss_prob=0.001, max_skips=0, output=False):
        '''
        Description: Configures the socket with the given parameters.
        Parameters:
            payload_size (int): the max payload size
            window (int): the window size
            timeout (float): the timeout value
            loss_prob (float): the probability of packet loss or ack loss
            max_skips (int): the maximum number of skips
            output (bool): whether to print packet info or not
        Returns: None
        '''
        self.size = payload_size
        self.window_size = window
        self.timeout = timeout
        self.loss_prob = loss_prob
        self.max_skips = max_skips
        self.output = output

    def send(self, payload, ack_num=0, syn_flag=0, ack_flag=0, fin_flag=0, reset_flag=0, res=True):
        '''
        Description: Sends a packet with the given payload and flags to the destination address.
        If the packet is not lost, it is added to the send buffer and the sequence number is updated.
        Parameters:
            payload (bytes): the payload to be sent
            ack_num (int): the ack number to be sent
            syn_flag (int): the SYN flag
            ack_flag (int): the ACK flag
            fin_flag (int): the FIN flag
            reset_flag (int): the RST flag
            res (bool): whether to print packet info or not
        Returns: None
        '''
        if ack_num == 0:
            ack_num = self.ack_num

        # Build packet and send it
        header = DRTPHeader(self.seq_num, ack_num, syn_flag,
                            ack_flag, fin_flag, reset_flag, self.window_size)
        packet = DRTPPacket(header, payload)

        # Simulate packet loss or ack loss
        skip = 0
        if self.num_skips < self.max_skips and not syn_flag:
            skip = random.randint(1, round(1 / self.loss_prob))
            if skip != 1:
                self.sock.sendto(packet.pack(), self.addr)
            else:
                if self.output:
                    if payload:
                        print('Lost packet with seq_num',
                              packet.header.seq_num)
                    else:
                        print('Lost ack for previous packet')
                self.num_skips += 1
        else:
            self.sock.sendto(packet.pack(), self.addr)

        # Print packet info if output is enabled
        if self.output and skip != 1 and res:
            print('ack_num {} seq_num {}, flags: ACK {}, SYN {}, FIN {}, RST {}, Data sent: {}'.format(
                ack_num, self.seq_num, ack_flag, syn_flag, fin_flag, reset_flag, len(payload)))

        # Add packet to send buffer and update seq_num
        if payload:
            self.send_buffer[self.seq_num] = packet
            self.seq_num += len(payload)
        if (syn_flag or fin_flag) and skip != 1:
            self.seq_num += 1

    def connect(self, addr):
        '''
        Description: Initiates a connection with the destination address.
        Parameters:
            addr (tuple): the destination address
        Returns (bool): True if connection is established, False otherwise 
        '''
        self.addr = addr
        # Send SYN
        self.send(b'', syn_flag=1)
        # Wait for SYN-ACK
        try:
            self.sock.settimeout(self.timeout)
            data, addr = self.sock.recvfrom(self.size + 12)
            packet = DRTPPacket.unpack(data)
            # Check if SYN-ACK is received and update ack_num
            if packet.header.syn_flag and packet.header.ack_flag:
                self.ack_num = packet.header.seq_num + 1
            else:
                raise socket.timeout
        except socket.timeout:
            print('Connection timed out')
            return False

        # Send ACK
        self.send(b'', ack_flag=1)
        self.addr = addr
        print('Connected to', addr)
        return True

    def listen(self):
        '''
        Description: Waits for a connection request from a client.
        Parameters: None
        Returns: None
        '''
        while True:
            # Wait for SYN
            while True:
                try:
                    self.sock.settimeout(self.timeout)
                    data, addr = self.sock.recvfrom(self.size + 12)
                    packet = DRTPPacket.unpack(data)
                    # Check if SYN is received and update ack_num
                    if packet.header.syn_flag:
                        self.ack_num = packet.header.seq_num + 1
                        self.addr = addr
                        break
                    else:
                        raise socket.timeout
                except socket.timeout:
                    continue

            # Send SYN-ACK
            self.send(b'', syn_flag=1, ack_flag=1)

            # Wait for ACK
            try:
                self.sock.settimeout(self.timeout)
                data, addr = self.sock.recvfrom(self.size + 12)
                packet = DRTPPacket.unpack(data)
                # Check if ACK is received
                if packet.header.ack_flag:
                    print('Connected to', addr)
                    break
            except socket.timeout:
                print('Connection timed out')
                continue

    def close(self):
        '''
        Description: Closes the connection with the destination address.
        Parameters: None
        Returns: None
        '''
        # Send FIN
        self.send(b'', fin_flag=1)
        # Wait for FIN-ACK
        while True:
            try:
                self.sock.settimeout(self.timeout)
                data, addr = self.sock.recvfrom(self.size + 12)
                packet = DRTPPacket.unpack(data)
                # Check if FIN-ACK is received
                if packet.header.ack_flag and packet.header.fin_flag:
                    break
                else:
                    raise socket.timeout
            except socket.timeout:
                # Resend FIN
                if self.output:
                    print('Resending FIN')
                self.send(b'', fin_flag=1)
                continue

        self.sock.close()  # close socket
        if self.output:
            print('Connection closed\n')
            print('Number of packets lost:', self.num_skips)

        self.num_skips = 0  # reset number of skips for another transfer

    def stop_and_wait(self, data):
        '''
        Description: Sends data using the stop-and-wait protocol.
        Parameters:
            data (bytes): the data to be sent 
        Returns: None
        '''
        # Send the first packet
        self.send(data[:self.size])

        seq_num = self.size  # next sequence number to be sent
        while seq_num < len(data):
            try:
                self.sock.settimeout(self.timeout)
                recv, addr = self.sock.recvfrom(self.size + 12)
                packet = DRTPPacket.unpack(recv)
                # Check if ACK is received
                if packet.header.ack_num == seq_num + 1:
                    # Check if there are more packets to be sent
                    if seq_num + self.size > len(data):
                        # Send the last packet
                        self.send(data[seq_num:], ack_flag=1)
                    else:
                        self.send(
                            data[seq_num:seq_num + self.size], ack_flag=1)

                    seq_num += self.size

            except socket.timeout:
                if self.output:
                    print('Resending packet with seq_num {}'.format(
                        seq_num - self.size + 1))
                # Resend the packet
                self.sock.sendto(
                    self.send_buffer[seq_num - self.size + 1].pack(), self.addr)
                continue

        if self.output:
            print('All packets sent')

        self.close()

    def go_back_n(self, data):
        '''
        Description: Sends data using the Go-Back-N protocol.
        Parameters:
            data (bytes): the data to be sent
        Returns: None
        '''
        # Send first window of packets
        for i in range(self.window_size):
            self.send(data[i *
                           self.size:(i + 1) * self.size], ack_flag=1)
            # Check if the last packet is smaller than the payload size
            if (i + 1) * self.size > len(data):
                self.send(data[i * self.size:], ack_flag=1)
                break

        # Wait for ACKs and send next window of packets if there are any
        seq_num = self.size
        while self.send_buffer:
            try:
                self.sock.settimeout(self.timeout)
                recv, addr = self.sock.recvfrom(self.size + 12)
                packet = DRTPPacket.unpack(recv)
                # Check if ACK is received
                if packet.header.ack_num == seq_num + 1:
                    # Check if there are more packets to be sent
                    if self.seq_num < len(data) + 1:  # +1 for SYN
                        start = self.seq_num - 1
                        if self.seq_num + self.size > len(data) + 1:
                            # send last packet
                            self.send(data[start:], ack_flag=1)
                        else:
                            self.send(
                                data[start:start + self.size], ack_flag=1)

                    # Remove the first packet from the send buffer (sliding window)
                    if len(self.send_buffer) > 1:
                        self.send_buffer.pop(seq_num - self.size + 1)
                    else:
                        self.send_buffer = {}

                    # Update seq_num
                    seq_num += self.size
                    if seq_num > len(data):
                        seq_num = len(data)

            except socket.timeout:
                # Resend all packets in the send buffer
                for seq_num_, packet in self.send_buffer.items():
                    self.sock.sendto(packet.pack(), self.addr)
                    if self.output:
                        print('Resending packet with seq_num', seq_num_)
                continue

        if self.output:
            print('All packets sent')

        self.close()

    def selective_repeat(self, data):
        '''
        Description: Sends data using the Go-Back-N protocol with Selective Repeat.
        Parameters:
            data (bytes): the data to be sent
        Returns: None
        '''
        # Send first window of packets
        for i in range(self.window_size):
            self.send(data[i * self.size:(i + 1) * self.size], ack_flag=1)
            # Check if the last packet is smaller than the payload size
            if (i + 1) * self.size > len(data):
                self.send(data[i * self.size:], ack_flag=1)
                break

        start = 0
        first = 1  # seq_num of the first packet in the send buffer
        while self.send_buffer:
            try:
                deadline = time.time() + self.timeout  # set deadline
                # Run while the first packet in the send buffer is not ACKed in a timeout period
                while first in self.send_buffer.keys():
                    # Check if timeout has occurred
                    if time.time() > deadline:
                        raise socket.timeout

                    self.sock.settimeout(self.timeout)
                    recv, addr = self.sock.recvfrom(self.size + 12)
                    packet = DRTPPacket.unpack(recv)

                    # Check if ACK is received and set a local seq_num variable
                    if packet.header.ack_num == len(data) + 1:
                        seq_num = packet.header.ack_num - len(data[start:])
                    else:
                        seq_num = packet.header.ack_num - self.size

                    # Check if the ACK is for some packet in the send buffer
                    if seq_num in self.send_buffer.keys():
                        # Check if there are more packets to be sent
                        if self.seq_num < len(data) + 1:  # +1 for SYN
                            start = self.seq_num - 1
                            if self.seq_num + self.size > len(data) + 1:
                                # Send last packet
                                self.send(data[start:], ack_flag=1)
                            else:
                                self.send(
                                    data[start:start + self.size], ack_flag=1)

                        # Remove packet from the send buffer (sliding window)
                        if len(self.send_buffer) > 1:
                            self.send_buffer.pop(seq_num)
                        else:
                            self.send_buffer = {}

                # If the first packet in the send buffer is ACKed, update first (seq_num)
                first += self.size

            except socket.timeout:
                # Resend first packet in the send buffer
                self.sock.sendto(
                    self.send_buffer[first].pack(), self.addr)
                if self.output:
                    print('Resending packet with seq_num', first)

        if self.output:
            print('All packets sent')

        self.close()

    def recv(self, protocol='saw'):
        '''
        Description: Receives data from the server.
        Parameters:
            protocol (str): the protocol to be used (saw: Stop and Wait, gbn: Go-Back-N, sr: Selective Repeat)
        Returns: None
        '''
        while True:
            try:
                data, addr = self.sock.recvfrom(self.size + 12)
                packet = DRTPPacket.unpack(data)
                # Check if packet is expected and send ACK
                if packet.header.seq_num >= self.ack_num:
                    # Check if packet is out of order
                    if packet.header.seq_num > self.ack_num:
                        if protocol in ['saw', 'gbn']:
                            if self.output:
                                print('Packet received out of order with seq_num',
                                      packet.header.seq_num)
                            continue
                        if protocol == 'sr':
                            pass

                    # Check if FIN is received and send ACK-FIN
                    if packet.header.fin_flag:
                        if self.output:
                            print('All packets received')
                        self.send(b'', ack_flag=1, fin_flag=1)
                        break
                    else:
                        # Add packet to the receive buffer
                        self.recv_buffer[packet.header.seq_num] = packet.payload
                        # Update ack_num and send ACK
                        self.ack_num = packet.header.seq_num + \
                            len(packet.payload)
                        self.send(b'', ack_flag=1)

                # Check if packet is already received and discard it
                elif packet.header.seq_num < self.ack_num:
                    res = False
                    # Check if packet is in the receive buffer, if not, add it
                    if packet.header.seq_num in self.recv_buffer:
                        if self.output:
                            print('Duplicate packet received with seq_num',
                                  packet.header.seq_num)
                        pass
                    else:
                        self.recv_buffer[packet.header.seq_num] = packet.payload
                        res = True  # print output

                    # Update ack_num and send ACK
                    ack_num = packet.header.seq_num + len(packet.payload)
                    self.send(b'', ack_num, ack_flag=1, res=res)

            except socket.timeout:
                continue

        self.sock.close()

        if self.output:
            print('Connection closed\n')
            print('Number of ack lost:', self.num_skips)

        self.num_skips = 0  # Reset number of skips for another transfer

        # Return received data in order
        data = b''
        for seq_num in sorted(self.recv_buffer.keys()):
            data += self.recv_buffer[seq_num]
        return data
