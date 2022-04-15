import pickle
import socket
import threading

from server.database import Database


class Receiver:
    def __init__(self, address, database):
        """Initiates the receiver with given address (udp)

        :param tuple address: Address (address, port) to start the receiver on
        :param Database database: The database to send from
        :rtype: None"""
        self._address = address
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._database = database  # Database

        self._shut_down = threading.Event()  # Off button for _update

    def _update(self):
        """Receives the data and stores it in database until stopped

        :rtype: None"""
        while not self._shut_down.isSet():  # While on
            data, _ = self._socket.recvfrom(4096)  # Receive data, don't care about address

            if data == b'exit':
                break

            station_id, temperature, precipitation = pickle.loads(data)  # Unpack data

            self._database.write(station_id, temperature, precipitation)  # Write data to database

        # Close socket and database
        self._socket.close()

    def start(self):
        """Starts the receiver on a separate thread

        :rtype: None"""
        self._socket.bind(('localhost', 0))

        threading.Thread(target=self._update).start()  # Starts thread that receives data and stores it

    def stop(self):
        """Stops the receiver

        :rtype: None"""
        self._shut_down.set()  # Stops thread that receives data

    @property
    def address(self):
        """Gets address

        :return: Address (address, port)
        :rtype: tuple"""
        return self._socket.getsockname()  # Returns data
