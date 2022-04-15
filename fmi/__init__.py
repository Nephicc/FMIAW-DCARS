import pickle
import re
from socket import socket, AF_INET, SOCK_STREAM
from typing import List, Union
import flask_implementation.app as app


class FMI:
    def __init__(self):
        """Initiates the FMI

        :rtype: None"""
        self._socket = socket(AF_INET, SOCK_STREAM)

        self._shut_down = False

        self._address = None

    def _update(self):
        """Constantly gets request from console

        :rtype: None"""
        while not self._shut_down:
            line = input('> ').split(' ')
            try:
                if len(line) > 1:
                    self._parse_cmd(line[0], line[1:])
                else:
                    self._parse_cmd(line[0])
            except OSError as e:
                print(f"Could not communicate with server: '{e}'")

        # Shutdown
        # Try to send shutdown message to server
        try:
            self._socket.send(b'exit')
        except OSError:
            pass

        self._socket.close()

    def start(self):
        """Starts FMI

        :rtype: none"""

        print('\rWelcome to FMI Console v0.2.14')

        print("See 'help' to get started.")

        self._update()

    def stop(self):
        """Stops FMI

        :rtype: None"""
        self._shut_down = True

    def _receive(self):
        """Receive data

        :rtype: bytes"""
        data = b''
        data = self._socket.recv(4096)
        while data[-3:] != b'EOF':
            data += self._socket.recv(4096)

        return data[:-3]  # Remove poison-pill from message

    def _parse_cmd(self, cmd, args=None):
        """Parses the cmd request and performs

        :param str cmd: Command entered in console
        :param List[str] args: Arguments for command
        :rtype: None"""
        cmd = cmd.lower()

        if len(cmd) == 0:
            pass
        elif cmd == 'help':
            self._print_help(args)
        elif cmd == 'get-data':
            self._get_data(args)
        elif cmd == 'start-webapp':
            self._start_webapp(args)
        elif cmd == 'connect':
            self._connect(args)
        elif cmd == 'status':
            self._status()
        elif cmd == 'exit':
            self._exit()
        elif cmd == 'clear':
            self._clear()
        else:
            self._cmd_not_found(cmd)

    @staticmethod
    def _cmd_not_found(cmd):
        """Action to perform if command is invalid

        :param str cmd: The command that was attempted
        :rtype: None"""
        print(f"Command '{cmd}' not found. See 'help'.")

    @staticmethod
    def _print_help(args):
        """Prints help text

        :param List[str] args: Arguments that accompanied command
        :rtype: None"""
        cmd = None
        if args is not None and len(args) == 1:
            cmd = args[0].lower()

        if cmd is None:
            print("FMI commands:")
        if cmd == 'help' or cmd is None:
            print("\tHELP [CMD]:\t\t\t\t\t\tPrints this help screen.")
        if cmd == 'get-data' or cmd is None:
            print("\tGET-DATA [FROM] [TO]:"
                  "\t\t\tFetches data from server using supplied indexes, default values are: 0, inf.")
        if cmd == 'start-webapp' or cmd is None:
            print("\tSTART-WEBAPP [ADDRESS:PORT]:\t\tStarts a webpage where data can be viewed in real time.")
        if cmd == 'connect' or cmd is None:
            print("\tCONNECT ADDRESS:PORT:\t\t\tAttempts to connect to a server using supplied address : port.")
        if cmd == 'status' or cmd is None:
            print("\tSTATUS:\t\t\t\t\t\t\tGives information about the current session.")
        if cmd == 'exit' or cmd is None:
            print("\tEXIT:\t\t\t\t\t\t\tExit the FMI console.")
        if cmd == 'clear' or cmd is None:
            print("\tCLEAR:\t\t\t\t\t\t\tClears connected database")

    def _get_data(self, args=None, print_data=True) -> Union[dict, None]:
        """Get data from index

        :param List[str] args: Command line arguments
        :param bool print_data: If the data should be printed
        :rtype: Dict{station_id: data} or None"""
        if args is None or len(args) == 0:
            self._socket.send(b'get-data')
        elif len(args) == 1:
            self._socket.send(f'get-data {args[0]}'.encode())
        elif len(args) == 2:
            self._socket.send(f'get-data {args[0]} {args[1]}'.encode())
        else:
            if print_data:
                print("Error, invalid argument given; see help.")
            return None

        # Receive data
        data = self._receive()

        if data == b'error':
            print("Server responded with error.")
            return None

        data = pickle.loads(data)

        if print_data:
            for station_id, info in data.items():
                print(f"Station {station_id} data:")
                for t, r in info:
                    print(f"\tTemperature: {t},\tRain: {r}")

    def _start_webapp(self, args=None):
        """Starts the web app
        For implementation check out flask_implementation folder

        :param List[str] args: Arguments
        :rtype: None"""
        print("If you want to exit the flask web application in the terminal press CTRL + C.\n")
        print("Then you will be returned to the FMI control-prompt")
        app.run(self._address)

    def _connect(self, args=None):
        """Connects FMI to given socket

        :param List[str] args: Arguments from command, should be address (localhost:1234)
        :rtype: None"""
        if len(args) == 1 and re.match(r"[a-zA-Z0-9.]+:\d+", args[0]):  # Matches 'alpha:digit'. e.g.: 'localhost:8080'
            addr = args[0].split(':')
            print(addr)
            self._address = (addr[0], int(addr[1]))
            self._socket.connect((addr[0], int(addr[1])))
            self._socket.send(b'gib')
        elif len(args) == 2 and args[1].isdigit():  # Else if?
            self._socket.connect((args[0], args[1]))
            self._socket.send(b'gib')
        else:
            print("Error, invalid argument given; see help.")
            return

    def _status(self):
        """Ask server for status (How many data points and how many stations) report

        :rtype: None
        """
        data = b''
        try:
            self._socket.send(b'status')

            data = self._receive()
        except OSError:
            print("Could not communicate with server.")
            pass

        print(data.decode())

    def _exit(self):
        """Shut down FMI

        :rtype: None"""
        print("Shutting down.")
        self._shut_down = True

    def _clear(self):
        """Empties connected database

        :rtype: None"""
        self._socket.send(b'clear')
        self._receive()


__all__ = ['FMI']  # Overwrites from fmi import *
