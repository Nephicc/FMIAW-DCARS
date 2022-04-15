# Fictional Meteorological Institute Automated Weather-Data Collection And Review System (FMIAW-DCARS)
Mandatory assignment in INF142 v21.

## Prerequisites
- Some computers (at least one).
- The python packages in [`requirements.txt`](requirements.txt).

## Installation
1. Python 3.8 (Not tested on other versions)
2. Download this repository.
3. `pip install -r requirements.txt`

## Running
`python main.py` to start all modules or `python station_main.py`, `python server_main.py` or
`python fmi_main.py ADDR PORT ID INTERVAL` to start separate modules independently. 


## Usage
The FMIAW-DCARS system contains three modules, **station**, **server** and **FMI**. The system allows for setting up
multiple stations connected to one server, and multiple FMI consoles that can read data from the server. All modules can
be started through separately or automatically by running `main.py`.  

### Station
The [*station module*](station/__init__.py) contains a networking wrapper for weather stations. The station networking
wrapper [`Station`](station/__init__.py) connects to a server instance, and sends data - Station ID, Temperature, Rain -
using `pickles` to preserve floating-point accuracy. The station networking wrapper handles starting and stopping of
the underlying weather station.

The wrapper will transmit data using UDP, at the same interval the station uses to read data.

To start the station module manually, run [`python station_main.py ADDR PORT ID INTERVAL`](station_main.py), and
terminated by writing `exit` in the console window. 

The arguments given to `python station main.py` are:
- `ADDR` string - The address to connect to, e.g. `localhost`, `127.0.0.1`.
- `PORT` int - The port to connect to, e.g. `26556`.
- `ID` int - Numerical station ID, e.g. `0`, `145`.
- `INTERVAL` int - The station's simulation interval, e.g. `1`.

### Server
The [*server module*](server/__init__.py) is split into several sub-modules. The [`Server`](server/__init__.py) class
creates a database connection (default database name is *StationData*), and creates *Sender* and *Receiver* instances as
needed.

The receiver & sender instances are used for connected stations and FMI consoles respectively. When a station initially
connects to the server, it sends a byte-encoded message `take`, telling the server to create a Receiver instance, and
return it's port to the station. The station will then start sending data.

The same applies with FMI Consoles, which send a byte-encoded message `gib`, and acquire a Sender instance to
interface against.

The server can be started manually by running [`python server_main.py`](server_main.py), and terminated by writing
`exit` in the console window.

**WARNING:** *On exit, the server might crash, but it does exit, so we left it.*

### FMI Console
The FMI console is the user interface to the FMIAW-DCARS system. When started through the main entrypoint
[`main.py`](main.py), the user must connect to the server manually with `connect localhost:5005`. The FMI Console can
also be started separately from the other modules using [`fmi_main.py`](fmi_main.py).
 Read the FMI Console's helpful `help` message on startup for more information.

By running the command `start-webapp` in the FMI Console, a web-server instance will be started. If you click the link
you will be sent to our FMI-homepage. If you want to see Temperature data at the different weather stations click
"Temp", and if you want to se rain data from the stations click "Rain".

The website supports real-time data review from all stations, which is updated automatically every 5
seconds. The update time can be changed for faster or slower updates in the javascript graph files (See the setInterval 
methods).

**WARNING:** *Due to software limitations, stations with different time-intervals will have their data misaligned on the
graph, but we don't really care.*