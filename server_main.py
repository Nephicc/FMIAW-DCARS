from server import Server

if __name__ == "__main__":
    s = Server(('0.0.0.0', 5005), 'test')
    s.start()
    go = True
    while go:
        cmd = input('> ')
        if cmd == 'exit':
            s.stop()
            go = False
