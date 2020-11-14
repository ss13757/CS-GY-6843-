from socket import *
import os
import sys
import struct
import time
import select
import binascii
import statistics
# Should use stdev

ICMP_ECHO_REQUEST = 8

class R_Stats:
    sentP = 0
    recievedP = 0
    minimumT = 999999999
    maximumT = 0
    totalT = 0

rtt = R_Stats

def checksum(string):
    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = (string[count + 1]) * 256 + (string[count])
        csum += thisVal
        csum &= 0xffffffff
        count += 2

    if countTo < len(string):
        csum += (string[len(string) - 1])
        csum &= 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer



def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    global rtt

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        # Fill in start

        # Fetch the ICMP header from the IP packet
        rtt.recievedP += 1
        Header = recPacket[20:28]
        icmp_Type, icmp_Code, checkSum, icmp_ID,icmp_Sequence = struct.unpack('bbHHh', Header)

        if icmp_ID == ID:
            numDoubleBytes = struct.calcsize("d")
            sent = struct.unpack("d", recPacket[28:28 + numDoubleBytes])[0]
            return timeReceived - sent


        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Get the right checksum, and put in the header

    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network  byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)


    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str


    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")


    # SOCK_RAW is a powerful socket type. For more details:   http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1):
    # timeout=1 means: If one second goes by without a reply from the server,  	# the client assumes that either the client's ping or the server's pong is lost
    global rtt
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Calculate vars values and return them
    # Send ping requests to a server separated by approximately one second
    delayStDev = []

    for i in range(0,4):
        delay = doOnePing(dest, timeout)
        if delay == "Request timed out.":
            print(delay)
        else:
            delay = delay * 1000
            delayStDev.append(delay)
            print(delay)
        time.sleep(1)  # one second
        if delay != "Request timed out.":
            if rtt.minimumT > delay:
                rtt.minimumT = delay
            if rtt.maximumT < delay:
                rtt.maximumT = delay
            rtt.totalT += delay

    if rtt.recievedP == 0:
        packet_recv = rtt.recievedP
        packet_sent = rtt.sentP
        packet_loss = 100
        packet_min = 0
        packet_max = 0
        packet_avg = 0.0
        stdev_var = (0, 0)

        vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),str(round(stdev(stdev_var), 2))]
        print("\n----%s Ping Information----" % dest)
        print(str(packet_sent) + "Transmitted Packets" + str(packet_recv) + "Received Packets, " + str(packet_loss) + "% Packets Lost")
        print("round-trip min/avg/max/stddev", vars)

        return vars
    else:
        packet_recv = rtt.recievedP
        packet_sent = rtt.sentP
        packet_min = rtt.minimumT
        packet_avg = rtt.totalT / rtt.recievedP
        packet_max = rtt.maximumT
        packet_loss = (rtt.sentP - rtt.recievedP) / rtt.sentP
        stdev_var = delayStDev

        vars = [str(round(packet_min, 2)), str(round(packet_avg, 2)), str(round(packet_max, 2)),
                str(round(stdev(stdev_var), 2))]
        print("\n----%s Ping Information----" % dest)
        print(str(packet_sent) + "Transmitted Packets" + str(packet_recv) + "Received Packets, " + str(packet_loss) + "% Packets Lost")
        print("round-trip min/avg/max/stddev", vars)


if __name__ == '__main__':
    ping("no.no.e")