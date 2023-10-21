from flask import Flask, request, render_template
from flask_cors import CORS
import evadb
import lark
import json

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
    
cursor = evadb.connect().cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods = ['POST'])
def execute():
    data = request.json['query']
    try:
        res = cursor.query(data).df()
        return res.to_json(orient ='records')
    except AssertionError:
        return {"error": "Please check your syntax"}, 500
    except lark.exceptions.UnexpectedToken:
        return {"error": "Unexpected token in your query or incomplete syntax"}, 500
    except Exception as e:
        return {"error": "Unexpected error occurred"}, 500

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
    return res.to_json(orient ='records')


@app.route('/tables', methods = ['GET'])
def get_tables():
    res = cursor.query("SHOW tables").df()
    lst = res.values.tolist()
    tables = [table for [table] in lst]

    return json.dumps(tables)

def run():
    return app



if __name__ == "__main__":
    app.run()         
