# -*- coding: utf-8 -*-

import socket
import errno
import select

class Context(object):
    pass

class Server(object):

    _context = None
    _socket = None

    def __init__(self, context, host, port, backlog=50):
        self._context = context
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setblocking(0)
        self._socket.bind((host, port))
        self._socket.listen(backlog)

    def AcceptSession(self):
        sessionSocket, sessionAddress = self._socket.accept()
        sessionSocket.setblocking(0)
        return Session(self._context, sessionSocket)

class Session(object):

    _context = None
    _socket = None
    
    def __init__(self, context, socket):
        self._context = context
        self._socket = socket
        self._socket.setblocking(0)

    def __del__(self):
        self.Destroy()

    def SetDestroy(self):
        pass

    def Destroy(self):
        self.SetDestroy()

    def AcceptStream(self):
        pass

class Client(Session):

    def __init__(self, context, host, port):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.setblocking(0)
        try:
            clientSocket.connect((host, port))
        except socket.error as e:
            if e.errno != errno.EINPROGRESS:
                raise
        super(Client, self).__init__(context, clientSocket)
