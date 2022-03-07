"""
Server written by:
Liam Bullock
"""

import socket
import sys
import datetime


def connection_setup():
    """ Sets up connection, making sure port number is within limit"""
    arguments = sys.argv
    portnum = int(arguments[1])
    if len(arguments) == 2:
        try:
            if portnum > 1024 and portnum <= 64000:
                portnum = int(arguments[1]) #need to check for alphabet?
        except:
            print("Error: Port number is not within given limit")
            exit()
    else:
        print("Error: Number of arguments inputted is incorrect")
        exit()
    print(portnum)
    return(portnum)



def create_bind_listen_socket(portnum):
    """Creates, binds and listens to the socket. This will only occur if it passes the error checks"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        print("Socket created")
    except:
        print("Error: Socket unable to be created")
        exit()
    try:
        s.bind(('', portnum))
        print ("Socket binded to %s" %(portnum))
    except:
        print("Error: Socket unable to be binded")
        exit()
    try:
        s.listen()
        print("Socket is now listening")
    except:
        print("Error: Socket unable to listen")

    return(s, portnum)




def accept_connection(s, portnum):
    """Accepts connection, creating a loop that will send the data, making sure it is of appropriate 
    lengths until the socket is closed."""
    while True:
        connection, address = s.accept()

        connection.settimeout(1)
        time = datetime.datetime.now()
        print("Socket is connected by port number: {0} of ip: {1} at [{2}]".format(portnum, address[0], time.strftime('%H:%M')))

        
        processFileCheck(connection)
        
        

  
  
def processFileCheck(connection):
    """Checks the fileprocces, making sure it is valid. If valid sends to processFile
    to be processed."""
    
    first_packet = connection.recv(1029) #max buffer for header (5 bytes) + filename length (1024)
    

    if len(first_packet) <= 5: #Only need first 5 to check the header
        print("Error: Packet header does not meet minimum required bytes")
        connection.close()
    else:
        #Check for correct header parts - before extracting
        magicNum = first_packet[0] << 8 | (first_packet[1] & 0xFF)
        fileLength = first_packet[3] << 8 | (first_packet[4] & 0xFF)   
        
        #Checks for valid magic number
        if magicNum != 0x497E:
            print("Error: Magic number is incorrect")
            connection.close()
        #Checks for valid Type number
        elif first_packet[2] != 1:
            print("Error: Type number is incorrect")
            connection.close()         
        #Checks for valid file length
        elif (1 > fileLength > 1024):
            print("Error: File length is not within 1 and 1024")
            connection.close()                
        #Sends to process file to be processed.
        else:
            processFile(connection, first_packet)




def processFile(client_s, first_packet):
    """Processes the files data"""
        
    
    filename = first_packet[5:].decode('utf-8')

    
             
    statusNumber = 1
    
    #Following are error checks for the file
    try:
        file = open(filename, "rb")
        processing_file = file.read()
        
    except BufferError as buffer_error:
        statusNumber = 0
        print("Error: Buffer error:", buffer_error)

    
    except OSError as os_error:
        statusNumber = 0
        print("Error: OS error:", os_error)
    

    except:
        statusNumber = 0
        print("Error: Client socket closed.")
        
        
    else:
        if len(processing_file) == 0:
            print("Error: File contains no data")
            statusNumber = 0
        

    magicNumber = 0x497E
    
    
    result = bytearray()
    
    result.append((magicNumber >> 8))
    result.append((magicNumber & 0xFF))
    result.append((0x2))
    result.append((statusNumber))
 
    if statusNumber == 0:
        #If status number is not correct then sends header only - no data inside
        client_s.send(result)
        
    else:
        #correct status number will cause the data to be processed ready to be sent
        result_bytes = bytearray(processing_file)                    
        data_length = len(result_bytes)
        
        result.append((data_length >> 24))
        result.append((data_length >> 16 & 0xFF))
        result.append((data_length >> 8 & 0xFF))
        result.append((data_length & 0xFF))   
        
        client_s.send((result + result_bytes))
        file.close()
        print("The total bytes transferred was: ", data_length)
        
    client_s.close()

def main():
    """Calls functions to get the server set up and listening."""
    portnum = connection_setup()
    s, portnum = create_bind_listen_socket(portnum)
    accept_connection(s, portnum)
    

main()