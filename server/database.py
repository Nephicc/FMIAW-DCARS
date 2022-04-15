import sqlite3
from threading import Lock


class Database:
    def __init__(self, database):
        """Starts the database with the given name

        :param str database: name of database
        :rtype: None
        """
        self._conn = sqlite3.connect(database, check_same_thread=False)  # Connects to database with name database
        self._cursor = self._conn.cursor()  # https://en.wikipedia.org/wiki/Cursor_(databases)

        self._lock = Lock()

        self._create_table()

    def _create_table(self):  # Creates database with cols
        """Creates the database table if it doesn't exist

        :rtype: None
        """
        with self._lock:
            self._cursor.execute("CREATE TABLE IF NOT EXISTS station_data ("
                                 "data_index INTEGER PRIMARY KEY AUTOINCREMENT, temperature FLOAT NOT NULL,"
                                 "precipitation FLOAT NOT NULL,station_id INTEGER DEFAULT 0);")
            self._conn.commit()

    def write(self, station_id, temperature, precipitation):
        """
        Writes row to database

        :param int station_id: Id of station data comes from
        :param float temperature: Temperature reading
        :param float precipitation: Precipitation reading
        :rtype: None
        """
        with self._lock:
            self._cursor.execute("INSERT INTO station_data (temperature, precipitation, station_id) VALUES (?, ?, ?);",
                                 (temperature, precipitation, station_id))
            self._conn.commit()

    def read(self, idx_from=0, idx_to=-1):  # Reads given row from database
        """Reads rows from index

        :param int idx_from: index to start from (inclusive)
        :param int idx_to: Index to stop read at
        :return: Dictionary of tuples(temp, prec) ordered by station_id.
        :rtype: dict
        """
        # Query for reading row
        query = "SELECT temperature, precipitation, station_id FROM station_data WHERE data_index >= ?"
        params = idx_from,

        if idx_to != -1:
            query += " AND data_index <= ?"
            params = idx_from, idx_to

        query += ';'  # End of query

        data = {}
        with self._lock:
            for row in self._cursor.execute(query, params):  # Copy data to list
                temp, rain, station = tuple(row)
                if station not in data:
                    data[station] = []
                data[station].append((temp, rain))

        return data

    def get_count(self):
        """
        Gets count of all datapoints in database.

        :return: Datapoint count
        :rtype: int
        """
        with self._lock:
            self._cursor.execute("SELECT COUNT(data_index) FROM station_data")

            return self._cursor.fetchone()[0]  # Only selecting one value

    def get_station_count(self):
        """
        Returns amount of stations in database.

        :return: Amount of stations
        :rtype: int
        """
        with self._lock:
            self._cursor.execute("SELECT COUNT(DISTINCT station_id) FROM station_data")

            return self._cursor.fetchone()[0]  # Only selecting one value

    def close(self):
        """Closes the sql connection

        :rtype: None
        """
        with self._lock:
            self._conn.close()

    def clear(self):
        with self._lock:
            self._cursor.execute("DELETE FROM station_data")
            self._conn.commit()
