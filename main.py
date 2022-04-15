import fmi
import server
import station


def main():
    # Create server
    srv = server.Server()
    srv.start()

    # Create station server
    st = station.Station(srv.address, 5)
    st.start()

    # Create FMI console
    cmd = fmi.FMI()
    cmd._connect(['localhost:5005'])  # shhh
    cmd.start()

    cmd.stop()
    srv.stop()
    st.stop()


if __name__ == "__main__":
    main()
