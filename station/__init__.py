import pickle
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM
import threading
from time import sleep

from station.station import StationSimulator


class Station:
    def __init__(self, server_addr, interval=1, station_id=0, start_hour=0):
        """Initiates station

        :param tuple server_addr: Address of station
        :param int interval: Interval of data updates in seconds
        :param int station_id: Id of station
        :param int start_hour: Hour to start simulation on
        :rtype: None"""
        self._socket = socket(AF_INET, SOCK_DGRAM)  # Creates socket
        self._server_address = server_addr  # Stores the address to send data

        self._id = station_id  # Stores the server address
        self._start_hour = start_hour

        self._interval = interval  # Stores the interval
        self._station = StationSimulator(simulation_interval=interval)  # Creates the station simulator

        self._shut_down = threading.Event()  # Event for shutdown

    def _update(self):
        """Constantly sends data to server

        :rtype: None"""
        while not self._shut_down.wait(self._interval):
            # Send serialized temperature and rain data to server.
            self._socket.sendto(pickle.dumps((self._id, self._station.temperature, self._station.rain)),
                                self._server_address)

        # Shut down station simulation
        self._station.shut_down()

    def start(self):
        """Start the station

        :rtype: None"""
        temp_sock = socket(AF_INET, SOCK_STREAM)

        temp_sock.connect(self._server_address)

        temp_sock.send(b'take')
        a = pickle.loads(temp_sock.recv(1024))
        self._server_address = a[0], a[1]
        temp_sock.close()

        self._station.turn_on(starting_hour=self._start_hour)  # Turns on simulator
        sleep(self._interval / 2)  # Wait for initial input

        threading.Thread(target=self._update).start()  # Start the sender on a new thread

    def stop(self):
        """Stops the station

        :rtype: None"""
        self._shut_down.set()


__all__ = ['Station']  # Overwrites from station import *
