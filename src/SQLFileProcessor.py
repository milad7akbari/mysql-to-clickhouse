import os
import re

from db.ClickhouseConnector import clickhouse_manager

class SQLFileProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.validate_file_extension()
        self.type_mapping = {
            'TINYINT': 'Int8',
            'SMALLINT': 'Int16',
            'MEDIUMINT': 'Int32',
            'INT': 'Int32',
            'INTEGER': 'Int32',
            'BIGINT': 'Int64',
            'FLOAT': 'Float32',
            'DOUBLE': 'Float64',
            'DECIMAL': 'Decimal(18, 2)',
            'DATE': 'Date',
            'DATETIME': 'DateTime',
            'TIMESTAMP': 'DateTime',
            'TIME': 'String',
            'YEAR': 'Int16',
            'CHAR': 'String',
            'VARCHAR': 'String',
            'TINYTEXT': 'String',
            'TEXT': 'String',
            'MEDIUMTEXT': 'String',
            'LONGTEXT': 'String',
            'BINARY': 'String',
            'VARBINARY': 'String',
            'TINYBLOB': 'String',
            'BLOB': 'String',
            'MEDIUMBLOB': 'String',
            'LONGBLOB': 'String',
            'ENUM': 'String',
            'SET': 'String',
            'JSON': 'String',
            'BOOLEAN': 'UInt8'
        }
        self.sql_string = ""
        self.order_by = []
        self.partition = []

    def validate_file_extension(self):
        _, file_extension = os.path.splitext(self.file_path)

        if file_extension not in ['.sql', '.txt']:
            raise ValueError("Invalid file type. Only .sql and .txt files are allowed.")
    def process_file(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        for line in lines:
            self.process_line(line.strip())

        queries = self.sql_string.split(';')
        total_queries, valid_queries = self.validate_queries(queries)
        print(f"Total Queries: {total_queries}")
        print(f"Valid Queries: {valid_queries}")
        print(f"Total Tables in Database: {clickhouse_manager.count_tables()}")

    def process_line(self, line):
        if match := re.match(r'^DROP\sTABLE.*\;', line, re.DOTALL):
            self.sql_string += match.group(0) + ' '
        elif match := re.match(r'^CREATE\sTABLE.*?\(', line, re.DOTALL):
            self.sql_string += match.group(0).replace('CREATE TABLE', 'CREATE TABLE IF NOT EXISTS') + ' '
        elif match := re.match(r'^(\`.*?\`)\s(\w+)', line, re.DOTALL):
            self.process_field(match.groups())
        if match := re.match(r'\`(.*?)\`\s.*AUTO_', line, re.DOTALL):
            self.order_by.append(match.group(1))
        elif match := re.match(r'PRIMARY\sKEY\s.*?\`(\w+)\`,?.*', line, re.DOTALL):
            self.order_by.append(match.group(1))
        elif match := re.match(r'.*INDEX.*\`(.*)\`\s.*', line, re.DOTALL):
            self.order_by.append(match.group(1))
        if match := re.match(r'^\)\sENGINE', line, re.DOTALL): 
            self.finalize_create_table()

    def process_field(self, groups):
        field_name, field_type = groups
        if field_type.upper() in ['DATE', 'DATETIME', 'TIMESTAMP']:
            self.partition.append(f'toYYYYMM({field_name})')
        elif field_type.upper() in ['TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER', 'BIGINT']:
            self.partition.append(field_name)

        self.sql_string += f"{field_name} {self.type_mapping.get(field_type.upper(), field_type)}, "

    def finalize_create_table(self):
        self.sql_string = self.sql_string.rstrip(', ') + ') ENGINE = MergeTree()'
        if self.partition:
            self.sql_string += f" PARTITION BY ({', '.join(set(self.partition))})"
        self.sql_string += f" ORDER BY ({', '.join(set(self.order_by)) if self.order_by else 'tuple()'})"
        self.sql_string += ';'
        self.partition.clear()
        self.order_by.clear()

    def validate_queries(self, queries):
        total_queries = 0
        valid_queries = 0
        for query in queries:
            query = query.strip()
            if query:
                total_queries += 1
                if re.match(r'^[a-zA-Z0-9\s!@#$%^&*()_+=\-;"\'<>,.?/\\|`~]*$', query):
                    valid_queries += 1
                    clickhouse_manager.execute(query)


        return total_queries, valid_queries


processor = SQLFileProcessor('../example.sql')
processor.process_file()