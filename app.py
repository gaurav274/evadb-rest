from flask import Flask, request, render_template
from flask_cors import CORS
import evadb
import lark
from enum import Enum
import json
import os
import uuid

from startup_steps import StartupSteps
from response import Response
from response import Type

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

class EvaDBConnector():
    def __init__(self):
        self.path = uuid.uuid4().hex
        self.cursor = evadb.connect(self.path).cursor()
    def run_startup_scripts(self):
        StartupSteps(self.cursor).run()

# cursor = evadb.connect().cursor()
# StartupSteps(cursor).run()

@app.before_request
def pre_req():
    evadb_connector = EvaDBConnector()
    print(evadb_connector.path)
    evadb_connector.run_startup_scripts()
    app.config["evadb_connector"] = evadb_connector

@app.after_request
def post_req(resp):
    evadb_connector = app.config["evadb_connector"]
    os.system("rm -r {path}".format(path=evadb_connector.path))
    app.config["evadb_connector"] = None
    return resp

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods = ['POST'])
def execute():
    try:
        evadb_connector = app.config["evadb_connector"]
        data = request.json['query']
        res = evadb_connector.cursor.query(data).df()
        return Response(data=res.to_json(orient='records'), type=Type.TABLE.name).generate()
    except AssertionError:
        return Response(msg = "Please check your syntax", type = Type.ERROR.name).generate(status=500)
    except lark.exceptions.UnexpectedToken:
        return Response(msg="Unexpected token in your query or incomplete syntax", type=Type.ERROR.name).generate(status=500)
    except Exception as e:
        return Response(msg="Unexpected error occurred", type=Type.ERROR.name).generate(500)

# @app.route('/create', methods = ['POST'])
# def create():
#     data = request.json['params']
#     query = """
#         CREATE DATABASE {name}
#         WITH ENGINE = '{engine}',
#         PARAMETERS = {{
#             "user": '{user}',
#             "password": '{password}',
#             "host": '{host}',
#             "port": '{port}',
#             "database": '{db}'
#         }};
#     """.format(name=data['name'], engine=data['engine'], user=data['user'], password=data['password'], host=data['host'], port=data['port'], db=data['db'])
#     res = cursor.query(query).df()
#
#     return Response(data = res.to_json(orient ='records'), type = Type.TABLE.name).generate()


@app.route('/schemas', methods = ['GET'])
def get_tables():
    try:
        tables = {}
        evadb_connector = app.config["evadb_connector"]

        """EvaDB """
        res = evadb_connector.cursor.query("SHOW tables").df()
        tables[DBEngine.EVADB.name] = [[json.loads(PostgresSchema(table_name, Columns(None, None)).json())] for [table_name] in res.values.tolist()]

        """Postgres """
        res = evadb_connector.cursor.query(
            """
                USE pg_db {
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema='public'
                    AND table_type='BASE TABLE'
                } 
            """
        ).df()

        tables[DBEngine.POSTGRES.name] = []
        tmp_table = []
        for [table_name] in res.values.tolist():
            res = evadb_connector.cursor.query(
                """
                    USE pg_db {{
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_schema='public'
                        AND table_name='{table_name}'
                    }}
                """.format(table_name=table_name)
            ).df()
            table_metadata = []
            for entry in res.values.tolist():
                table_metadata.append(PostgresSchema(table_name, Columns(entry[0], entry[1])).json())
            tmp_table.append(table_metadata)

        # Writing this piece of code to manage parsing issue
        # for some reason, objects are being treated as string is json.dumps is used
        # In future need to get rid of this logic
        for entry in tmp_table:
            table_metadata = []
            for record in entry:
                if type(record) is str:
                    table_metadata.append(json.loads(record))
            tables[DBEngine.POSTGRES.name].append(table_metadata)
        return Response(data = [tables], type = Type.SCHEMA.name).generate()
    except Exception as e:
        return Response(msg="Unexpected error occurred", type=Type.ERROR.name).generate(500)



class Columns():
    def __init__(self, column_name, column_type):
        self.column_name = column_name
        self.column_type = column_type

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True)

class PostgresSchema():
    def __init__(self, table_name, columns):
        self.table_name = table_name
        self.columns = columns

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True,)

class DBEngine(Enum):
    EVADB = 1
    POSTGRES = 2

if __name__ == "__main__":
    app.run()
