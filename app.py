from flask import Flask, request, render_template
from flask_cors import CORS
import evadb
import lark
import json

from response import Response
from response import Type

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
    
cursor = evadb.connect().cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods = ['POST'])
def execute():
    try:
        data = request.json['query']
        res = cursor.query(data).df()
        return Response(data=res.to_json(orient='records'), type=Type.TABLE.name).generate()
    except AssertionError:
        return Response(msg = "Please check your syntax", type = Type.ERROR.name).generate(status=500)
    except lark.exceptions.UnexpectedToken:
        return Response(msg="Unexpected token in your query or incomplete syntax", type=Type.ERROR.name).generate(status=500)
    except Exception as e:
        return Response(msg="Unexpected error occurred", type=Type.ERROR.name).generate(500)

@app.route('/create', methods = ['POST'])
def create():
    data = request.json['params']
    query = """
        CREATE DATABASE {name}
        WITH ENGINE = '{engine}',
        PARAMETERS = {{
            "user": '{user}',
            "password": '{password}',
            "host": '{host}',
            "port": '{port}',
            "database": '{db}'
        }};
    """.format(name=data['name'], engine=data['engine'], user=data['user'], password=data['password'], host=data['host'], port=data['port'], db=data['db'])
    res = cursor.query(query).df()

    return Response(data = res.to_json(orient ='records'), type = Type.TABLE.name).generate()


@app.route('/tables', methods = ['GET'])
def get_tables():
    res = cursor.query("SHOW tables").df()
    lst = res.values.tolist()
    tables = [table for [table] in lst]

    return Response(data = tables, type = Type.TABLE.name).generate()

if __name__ == "__main__":
    app.run()         
