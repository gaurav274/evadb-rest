import os
class StartupSteps():
    def __init__(self, cursor):
        self.cursor = cursor

    def run(self):
        self.initialize_db()

    def initialize_db(self):
        try:
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
        except Exception as e:
            pass


