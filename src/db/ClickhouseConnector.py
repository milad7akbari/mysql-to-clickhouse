from clickhouse_driver import Client


class ClickhouseConnector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ClickhouseConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self, host, port, username, password, database):
        if not hasattr(self, 'client'):
            self.client = Client(
                host=host,
                port=port,
                user=username,
                password=password,
                database=database
            )
            self.database = database

    def drop_all_tables(self):
        tables = self._get_all_tables()
        for table_name in tables:
            self.drop_table(table_name)

    def drop_table(self, table_name):
        if self._table_exists(table_name):
            drop_query = f"DROP TABLE IF EXISTS {self.database}.{table_name}"
            self.client.execute(drop_query)
            print(f"Table {table_name} dropped.")
        else:
            print(f"Table {table_name} does not exist.")

    def truncate_table(self, table_name):
        if self._table_exists(table_name):
            truncate_query = f"TRUNCATE TABLE {self.database}.{table_name}"
            self.client.execute(truncate_query)
            print(f"Table {table_name} truncated.")
        else:
            print(f"Table {table_name} does not exist.")

    def execute(self, query):
        try:
            self.client.execute(query)
        except Exception as e:
            print(f"Error executing query: {e}")

    def count_tables(self):
        tables = self._get_all_tables()
        count = len(tables)
        print(f"Total tables: {count}")
        return count

    def _get_all_tables(self):
        query = f"SELECT name FROM system.tables WHERE database = '{self.database}'"
        tables = self.client.execute(query)
        return [table[0] for table in tables]

    def _table_exists(self, table_name):
        query = f"SELECT count() FROM system.tables WHERE database = '{self.database}' AND name = '{table_name}'"
        count = self.client.execute(query)[0][0]
        return count > 0


# Configuration
host = 'localhost'
port = 9000
username = 'default'
password = ''
database = 'default'

clickhouse_manager = ClickhouseConnector(host, port, username, password, database)
