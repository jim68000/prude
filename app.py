from flask import Flask
import psycopg2

conn = psycopg2.connect('postgres://localhost')

conn.set_session(readonly=True)
conn.set_client_encoding('UTF8')

cur = conn.cursor()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/v1/schemas')
def get_schemas():
    cur.execute("select schema_name from information_schema.schemata;")
    schemas = [s[0] for s in cur.fetchall() if not s[0].startswith("pg_")]
    schemas.remove('information_schema')
    return str(schemas)


@app.route('/api/v1/tables/<schema>')
def get_tables(schema):
    cur.execute("select table_name from information_schema.tables where table_schema = '" + schema + "'")
    tables = cur.fetchall()
    return str(tables)

@app.route('/api/v1/columns/<schema>/<table>')
def get_columns(schema, table):
    cur.execute("select column_name, data_type  from information_schema.columns where table_schema = '" + schema + "' and table_name = '" + table + "'")
    tables = cur.fetchall()
    return str(tables)


if __name__ == '__main__':
    app.run()
