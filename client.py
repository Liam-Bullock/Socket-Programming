"""
Server written by:
Liam Bullock
"""

import socket
import sys
import os
import math

def connection_setup():
    """Sets up connection by getting the 3 inputs from the commandline."""
    arguments = sys.argv
    filename = arguments[3]
    if len(arguments) == 4:
        try:
            portnum = int(arguments[2]) 
        except:
            print("Error: Port number is not valid")
            exit()
        else:
            if (portnum < 1024 or portnum > 64000):
                print("Error: Port number is not within given limit")
                exit()
        try:
            ip_address = socket.gethostbyname(arguments[1])
        except:
            print("Error: IP/hostname not valid")
            exit()
            
        if os.path.isfile(arguments[3]):
            print("Error: File already exists")
            exit()
    else:
        print("Error: Number of arguments inputted is incorrect")
        exit()
        

    return(ip_address, portnum, filename)

def create_socket(ip, portnumber):
    """Creates IPV4 socket"""
    try:
        client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Socket created")
    except:
        print("Error: Socket unable to be created")
        exit()
              
    return(client_s)
    
    


def connect_socket(client_s, ip, portnumber):
    """Connects socket to port number given)"""
    try:
        client_s = client_s.connect((ip, portnumber))
        print("Socket successfully connected")
    except:
        print("Error: Unable to connect to server")
        exit()        



def fileRequest(file, client_s): 
    """Sends the file request to the server"""
    magicNum = 0x497E
    filename_bytes = file.encode('utf-8')
    filenamelength = len(filename_bytes)
    
    result = bytearray()
    
    result.append((magicNum >> 8))
    result.append((magicNum & 0xFF))
    result.append((0x01))
    result.append((filenamelength >> 8))
    result.append((filenamelength & 0xFF))    
        
    request = result + bytearray(filename_bytes)
    client_s.send(request)
    
    

def fileResponseCheck(filename, client_s):
    """Checks the validity of the header, if valid then sends to readData for data transfer"""
       
    try:
        packet_received = client_s.recv(8) #only need the first 8 to check the header
        if len(packet_received) == 0:
            raise ValueError("Error: Receiving file request")

    
    except ValueError as e:
        print("Error: Receiving file request")
        client_s.close()
        sys.exit()        
    

        
    if packet_received[3] == 0: 
        print("Error: Requesting the file")
        client_s.close()    
        sys.exit()
      
    else:
        if len(packet_received) < 8: 
            print("Error: Packet header does not meet minimum required bytes")
            client_s.close()
            sys.exit()
        else:
            #Check for correct header parts - before extracting
            magicNum = packet_received[0] << 8 | (packet_received[1] & 0xFF)
    
            if magicNum != 0x497E:
                print("Error: Magic number is incorrect")
                client_s.close()
                sys.exit()
            elif packet_received[2] != 2:
                print("Error: Type number is incorrect")
                client_s.close()      
                sys.exit()
            elif (packet_received[3] != 1):
                print("Error: StatusCode is incorrect")
                client_s.close()    
                sys.exit()
            else:
                return(packet_received)

    
    
    
    
    
def readData(datalength, filename, client_s):
    """Gets all the data in the file, if successful passes data onto writeFile to
    write into the new file."""
    
    #Bitmasking to find the data length in the header
    
    filedatalength = datalength[4] << 24 | datalength[5] << 16 | \
    datalength[6] << 8 | datalength[7] 
    
    
    resultFile = open(filename, 'wb')
    
    #Creates a count to dictate how many times the buffer needs to be sent
    count = math.ceil(filedatalength / 4096)
    
    #Stores the data that is recieved 
    data_recieved = bytearray()
    
    #Creates a variable to store the bytes recieved - used for error checking
    bytes_recieved = 0
    
    client_s.settimeout(1)
    
    #iterates through until the count is 0 - i.e until all the data is sent
    while count > 0:
        try:
            count -= 1
            tempdata = client_s.recv(4096) 
            bytes_recieved += len(tempdata)
            data_recieved += tempdata
        except client_s.timeout as timeout_error:
            print("Error: Socket timed out", timeout_error)
            client_s.close()
            exit()
    
        except:
            client_s.close()    
            sys.exit()
        

    
    if bytes_recieved != filedatalength:
        print("Error: reading file data")
        client_s.close()    
        sys.exit()                   
    else:
        print("The total bytes recieved was: ", bytes_recieved)
        return(data_recieved, resultFile)


def writeData(data, file, client_s):
    """Writes data into new file"""
    

    file.write(data)
    file.close()
    client_s.close()    
    sys.exit()               

    
def main():
    """Calls each function that is run through the client"""
    ip, portnumber, filename = connection_setup()
    
    client_s = create_socket(ip, portnumber)
    
    new = connect_socket(client_s, ip, portnumber)
    
    fileRequest(filename, client_s)
    
    file_data = fileResponseCheck(filename, client_s)
    
    Data_to_write, file = readData(file_data, filename, client_s)
    
    writeData(Data_to_write, file, client_s)

main()