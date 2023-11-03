import os
class StartupSteps():
    def __init__(self, cursor):
        self.cursor = cursor

    def run(self):
        self.initialize_db()

    def initialize_db(self):
        try:
            self.execute_common_queries()
            if os.environ["FLASK_ENV"] == "production":
                self.cursor.query(
                    """
                        CREATE DATABASE pg_db
                        WITH ENGINE = 'postgres',
                        PARAMETERS = {
                            "host": 'test-bed.postgres.database.azure.com',
                            "port": '5432',
                            "database": 'postgres',
                            "user": 'readonly@test-bed',
                            "password": 'password'}
                    """
                ).df()
            else:

                # development
                self.cursor.query(
                    """
                        CREATE DATABASE pg_db
                        WITH ENGINE = 'postgres',
                        PARAMETERS = {
                            "host": 'localhost',
                            "port": '5432',
                            "database": 'postgres',
                            "user": 'postgres',
                            "password": 'password'}
                    """
                ).df()
        except Exception as e:
            print(e)

    def execute_common_queries(self):
        self.cursor.query(
            """
                CREATE TABLE GOT (
                    id INTEGER UNIQUE,
                    house TEXT(50),
                    quote TEXT(50)
                );
            """
        ).df()

        self.cursor.query(
            """
                INSERT INTO GOT (id, house, quote) VALUES
                (1, 'Baratheon', 'Ours is the Fury'),
                (2, 'Greyjoy', 'We Do Not Sow'),
                (3, 'Martell', 'Unbowed, Unbent, Unbroken'),
                (4, 'Stark', 'Winter Is Coming'),
                (5, 'Tully', 'Family, Duty, Honor'),
                (6, 'Tyrell', 'Growing Strong'),
                (7, 'Lannister', 'Hear Me Roar!')
            """
        ).df()


