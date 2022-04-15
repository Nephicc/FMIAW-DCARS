from fmi import FMI


def main():
    console = FMI()
    console.start()

    console.stop()


if __name__ == '__main__':
    main()
