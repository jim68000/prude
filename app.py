from flask import Flask, render_template, request, session
import psycopg2
import json

conn = psycopg2.connect('postgres://localhost')
conn.set_session(readonly=True)
conn.set_client_encoding('UTF8')

cur = conn.cursor()

app = Flask(__name__)
app.secret_key = '76tv6rcs3x32azx43scrfybyuniu'


@app.route('/')
def hello_world():
    schemas = get_schemas()
    return render_template("home.html", schemas=schemas)


@app.route('/schemas')
def get_schemas():
    cur.execute("select schema_name from information_schema.schemata;")
    schemas = [s[0] for s in cur.fetchall() if not s[0].startswith("pg_")]
    schemas.remove('information_schema')
    session['schemas'] = schemas
    return schemas


@app.route('/explore/<schema>/tables')
def get_tables(schema):
    cur.execute("select table_name from information_schema.tables where table_schema = '" + schema + "'")
    tables = [t[0] for t in cur.fetchall()]
    print(session['schemas'])
    return render_template("home.html", schemas=session['schemas'], tables=tables, focussed_schema=schema)


@app.route('/explore/<schema>/<table>/columns')
def get_columns(schema, table):
    cur.execute("select column_name, data_type  from information_schema.columns where table_schema = '" + schema + "' and table_name = '" + table + "'")
    tables = cur.fetchall()
    columns = [c for c in tables]
    return render_template("home.html", schemas=[schema], tables=[table], columns=columns)


@app.route('/trivial')
def test_gov():
    return render_template('data_workspace.html')


@app.route('/process', methods=['POST'])
def process():
    cur.execute(request.form['sql'])
    rows = cur.fetchmany(1000)
    columns = [a.name for a in cur.description]
    return render_template('data_workspace.html', columns=columns, rows=rows, length=len(rows), sql=request.form['sql'])

if __name__ == '__main__':
    app.run()
