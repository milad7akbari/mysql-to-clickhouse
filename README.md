# MySQL to ClickHouse

**mysqltoclickhouse** is a tool to seamlessly convert MySQL database structures to ClickHouse.

## Features
- Convert MySQL table schemas to ClickHouse.
- Handle data type mappings.
- Provide example schemas for reference.

## Installation
- Clone the repository and install the dependencies:

## bash
- git clone https://github.com/milad7akbari/mysqltoclickhouse.git
- cd mysql-to-clickhouse-main
- pip install -r requirements.txt

## Usage Instructions
Dump MySQL Table Structure:
- Open the tables you need in the Navicat software and dump them (table structure only).
- Save the dumped tables in a .sql file.
- Place the example.sql file in the root directory of the project.

## Configure ClickHouse Connection:
- In the db folder, update the ClickhouseConnector file with your database specifications.
- This file contains methods for common database operations. Modify them if necessary and commit the changes.

## Run the Script:
- Finally, execute the code by selecting the path to your example.sql file. The script will store the structure of all MySQL tables in the ClickHouse database.

## Reporting Issues
- If you encounter any bugs or issues, please report them so we can address and fix them promptly.
