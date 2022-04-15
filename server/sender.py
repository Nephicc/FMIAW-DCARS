import pickle
from socket import socket
import threading

from server.database import Database


class Sender:
    def __init__(self, sock: socket, database: Database):
        """Initiates the sender with given address (tcp)

        :param socket sock: Address (address, port) to start tcp connection on
        :param Database database: The database to send from
        :rtype: None"""
        self._socket = sock

        self._database = database

        self._shut_down = threading.Event()

    def _parse_tcp(self, data):
        """Parses the request, gets the requested data from the database and returns the data as bytes

        :param str data: The request
        :return: The requested data in bytes
        :rtype: bytes"""
        data = data.split(' ')
        cmd = data[0].lower()

        args = []
        if len(data) > 1:
            args = data[1:]

        if cmd == 'get-data':
            if len(args) == 0:
                station_data = self._database.read()
            elif len(args) == 1 and args[0].isdigit():
                station_data = self._database.read(int(args[0]))
            elif len(args) == 2 and all(x.isdigit() for x in args):
                station_data = self._database.read(int(args[0]), int(args[1]))
            else:
                return b'error'
                
            return pickle.dumps(station_data)
        elif cmd == 'status':
            return "Database contains {} data points from {} unique stations."\
                .format(self._database.get_count(), self._database.get_station_count()).encode()
        elif cmd == 'exit':
            return b'exit'
        elif cmd == 'clear':
            self._database.clear()
            return b''
        else:
            return b'error'

    def _update(self):
        """Constantly receives requests and sends the requested data back

        :rtype: None"""
        while not self._shut_down.isSet():
            # Database read
            try:
                data = self._socket.recv(4096)  # Receives request TODO add timeout for shutdown check
            except ConnectionResetError:
                print("A fmi somewhere closed")
                break

            resp = self._parse_tcp(data.decode())
            if resp == b'exit':
                self.stop()
            else:
                self._socket.send(resp + b'EOF')  # Responds with data

        # Closes socket and database when done
        self._socket.close()

    def start(self):
        """Starts the sender

        :rtype: None"""
        threading.Thread(target=self._update).start()

    def stop(self):
        """Stops sender

        :rtype: None"""
        self._shut_down.set()

    @property
    def address(self):
        """Address sender is on

        :return: Address of sender (address, port)
        :rtype: tuple"""
        return self._socket.getsockname()
