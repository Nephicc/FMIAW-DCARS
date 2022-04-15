from server.receiver import Receiver
from server.sender import Sender
from server.database import Database
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import pickle


class Server:
    def __init__(self, address=("localhost", 5005), database_name='StationData'):
        """Initiates a server with udp receiver and tcp sender

        :param tuple address: address to receive request on
        :param str database_name: name of database to connect to
        :rtype: None"""
        self._senders = list()
        self._receivers = list()
        self._database = Database(database_name)
        self._sock = socket(AF_INET, SOCK_STREAM)
        self._address = address
        self._sock.bind(address)

    def start(self):
        """Starts the server's receiver and sender

        :rtype: None"""
        Thread(target=self.connect).start()

    def stop(self):
        """Stops the server's receiver and sender

        :rtype: None"""
        for addr in self._senders:
            addr.stop()

        for addr in self._receivers:
            with socket(AF_INET, SOCK_DGRAM) as sock:
                sock.sendto(b'exit', addr.address)
            addr.stop()

        self._database.close()

        with socket(AF_INET, SOCK_STREAM) as s:
            try:
                s.connect(self._sock.getsockname())
                s.send(b'exit')
            except OSError:
                pass

    def open_sender(self, conn):
        """Opens sender that takes commands and returns data

        :return: Address of sender started
        :rtype: tuple"""
        send = Sender(conn, self._database)
        send.start()
        self._senders.append(send)
        return send.address

    def open_receiver(self):
        """Opens receiver that receives data from stations

        :return: Address of receiver started
        :rtype: tuple"""
        rec = Receiver(("localhost", 0), self._database)
        rec.start()
        self._receivers.append(rec)
        return rec.address

    def close_sender(self, address):
        """Closes sender with given address

        :param tuple address: Address of sender to close
        :rtype: None"""
        for add in self._senders:
            if add.address == address:
                add.stop()
                self._senders.remove(add)

    def close_receiver(self, address):
        """Closes receiver with given address

        :param tuple address: Address of receiver to close
        :rtype: None"""
        for add in self._receivers:
            if add.address == address:
                add.stop()
                self._receivers.remove(add)

    def connect(self):
        """Constantly accepts requests for senders and receivers

        :rtype: None"""
        while True:
            self._sock.listen()
            conn, addr = self._sock.accept()
            data = conn.recv(1024)
            if data.decode() == 'exit':
                print("SERVER: Received stop-signal.")
                self._sock.close()
                conn.close()
                return
            if data.decode() == 'gib':
                print(f"SERVER: Creating sender for {addr}.")
                self.open_sender(conn)
            elif data.decode() == 'take':
                print(f"SERVER: Creating receiver for {addr}.")
                conn.send(pickle.dumps(self.open_receiver()))

    def get_index(self):
        """Returns highest index in database

        :return: Highest index in database
        :rtype: int"""
        return self._database.get_count()

    @property
    def address(self):
        """returns address that server uses to handle requests

        :return: Address (IP, PORT) of request handler
        :rtype: tuple"""
        return self._address


__all__ = ['Server']  # Overwrites from server import *
