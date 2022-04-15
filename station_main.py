import sys
from station import Station

if __name__ == "__main__":
    print("Starting...")
    s = Station((sys.argv[1], int(sys.argv[2])), station_id=int(sys.argv[3]), interval=int(sys.argv[4]))
    s.start()
    print("Started.")
    go = True
    while go:
        cmd = input('> ')
        if cmd == 'exit':
            s.stop()
            go = False
