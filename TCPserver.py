#############################################################################
# Program:
#    Lab PythonWebServer, Computer Networks
#    Brother Jones, CSE354
# Author:
#    Jeremy Duong
# Summary:
#    This is my implementation of the TCP server for lab02
#    Function getHTTPResponse() was created to craft 1 http response
#       to be sent back to the client by the server. Within this function,
#       the http response message is created manually without the help of
#       any outside library.
#
##############################################################################

#############################################################################
# Take 1:
#    It took me about 5 hours to figure everything out but I finally got
#    everything pretty much working... I think. 
#    The style might not be the best though.
#
#    I didn't have enough time to create a new thread for every different
#    connection from a different host. But if I have enough time, I would
#    certainly do this since it prevents blocking (one client's connection
#    preventing other clients to connect to the server)
#
##############################################################################
from socket import *
import sys
import os
import http

CRLF = "\n\n" #For some reason, the \r doesn't work, but the \n does...

# Return proper content type
def contentType(filepath):
    # Based on the file extension, return the content type
    # that is part  of the "Content-type:" header"
    extension = filepath.split(".")[1]
    if extension == "gif":
        return "image/gif"
    elif extension == "jpg":
        return "image/jpg"
    elif extension == "html":
        return "text/html"
    elif extension == "txt":
        return "text/plain"
    else:
        return "text/plain"

# Craft all the info from the request into ONE response to rule them all :)
def getHTTPResponse(filePath, fileExists, httpVersion):
    #  -create the status line and put it in the response
    status = 404 if not fileExists else 200
    sttString = str(status) + " " + ("OK" if status == 200 else "Not Found")
    response = httpVersion + b" " + str(status).encode() + b" " + sttString.encode() + b"\n"

    #  -create the "Content-type:" header and put it in the response
    if status == 200:
        content_type = contentType(filePath)
    else:
        content_type = "text/html"
    response += b"Content-Type: " + content_type.encode()

    #  -What goes between the header lines and the requested file?
    response += CRLF.encode()  # this :|

    #  -send the file or 404 message
    if status == 404:
        response += b"<h1>404 - Request Not Found!<h1>"
        response += b"<h5>(This message was personally crafted by Jeremy Duong lol :D)<h5>"
    elif status == 200:
        #     -open a file in binary like ... = open(filepath, "rb")
        with open("./" + filePath, "rb") as f:
            line = f.readline()
            while (line):
                response += line
                line = f.readline()
    else:
        response += b"Status: " + str(status).encode()

    return response


# Server Connection Setup
serverPort = int(sys.argv[1]) if len(sys.argv) == 2 else 6789
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print("Server is running on port ", str(serverPort))

try:
    # Main Server Loop (This is the most messy server in the world, but oh well...)
    while 1:
        # Things to be done include:
        #  -accept a connection
        connectionSocket, addr = serverSocket.accept()

        #  -read the request (if an empty request ignore it)
        request = connectionSocket.recv(1024).decode()
        httpMessageLines = request.split('\n')

        #The first line of the http message is the request line, print to console
        print(httpMessageLines[0])
        
        #  -parse token from the request string, including: filePath and httpVersion
        filePath = "/"
        httpVersion = "HTTP/1.1"
        if (len(httpMessageLines) > 0 and len(httpMessageLines[0]) > 0):
            filePath = httpMessageLines[0].split(' ')[1]
            httpVersion = httpMessageLines[0].split(' ')[2].encode()
        else:
            connectionSocket.close() # If receive an empty httpRequest, just close
            continue                 #  and... move on to the next iteration

        # When there's nothing for the request file, 
        #    how about we make bufbomb.html the home page?
        if (filePath == "/"):
            filePath = "bufbomb.html" 
        
        # If there is not just a '/' but it does start with a '/', take it out.
        #    This is because open() doesn't work if there is a '/' in front
        elif (filePath[0] == '/'):
            filePath = filePath[1:]

        #  -make sure the file exists
        #     -all files are to be relative to the directory
        #      in which the web server was started
        fileExists = os.path.exists(filePath)

        # base on the filePath, whether the file exists, and the httpVersion,
        #   craft a binary response to be sent
        response = getHTTPResponse(filePath, fileExists, httpVersion)

        # Finally :( after all the hard work (T_T) I can now send the response...
        connectionSocket.send(response)

        #  -don't forget to close the connection socket
        connectionSocket.close()


except KeyboardInterrupt:
    print("\nClosing Server")
    serverSocket.close()
    quit()
