from flask import Flask, render_template, request, session
import psycopg2 

conn = psycopg2.connect('postgres://localhost')
conn.set_session(readonly=True, autocommit=True)
conn.set_client_encoding('UTF8')

cur = conn.cursor()

app = Flask(__name__)
app.secret_key = '76tv6rcs3x32azx43scrfybyuniu'


@app.route('/')
def start_page():
    return render_template('sql_editor.html')


@app.route('/schemas')
def get_schemas():
    cur.execute("select schema_name from information_schema.schemata;")
    schemas = [s[0] for s in cur.fetchall() if not s[0].startswith("pg_")]
    schemas.remove('information_schema')
    session['schemas'] = schemas
    return render_template("schema_explorer.html", schemas=schemas)


@app.route('/explore/<schema>/tables')
def get_tables(schema):
    cur.execute("select table_name from information_schema.tables where table_schema = '" + schema + "'")
    tables = [t[0] for t in cur.fetchall()]
    session[schema] = tables
    return render_template("table_explorer.html", tables=tables, focussed_schema=schema)


@app.route('/explore/<schema>/<table>/columns')
def get_columns(schema, table):
    cur.execute(
        "select column_name, data_type  from information_schema.columns where table_schema = '" + schema + "' and table_name = '" + table + "'")
    columns = cur.fetchall()
    columns = [c for c in columns]
    cur.execute('select count(*) from "' + schema + '"."' + table + '";')
    items = cur.fetchone()[0]
    return render_template("column_explorer.html",
                           schemas=session['schemas'],
                           tables=session[schema],
                           columns=columns,
                           focussed_schema=schema,
                           focussed_table=table,
                           items=items)


@app.route('/process', methods=['POST'])
def process():
    try:
        cur.execute(request.form['sql'])
        rows = cur.fetchmany(1000)
        columns = [a.name for a in cur.description]
        return render_template('sql_editor.html', columns=columns, rows=rows, length=len(rows), sql=request.form['sql'])
    except psycopg2.Error as e:
        return render_template('sql_editor.html', error=e.pgerror, sql=request.form['sql'])


@app.route('/view100/<table>')
def view_100(table):
    try:
        sql = 'select * from ' + table + ' limit 100;'
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [a.name for a in cur.description]
        return render_template('sql_editor.html', columns=columns, rows=rows, length=len(rows), sql=sql)
    except psycopg2.Error as e:
        return render_template('sql_editor.html', error=e.pgerror, sql=sql)


@app.route('/start/<schema>/<table>')
@app.route('/start/<schema>/<table>/<column>')
def start_sql_table(schema, table, column=None):
    try:
        col = '*'
        if column:
            col = column
        sql = f"select {col} from \"{schema}\".\"{table}\""
        cur.execute(sql)
        rows = cur.fetchmany(1000)
        columns = [a.name for a in cur.description]
        return render_template('sql_editor.html', columns=columns, rows=rows, sql=sql)
    except psycopg2.Error as e:
        return render_template('sql_editor.html', error=e.pgerror, sql=sql)

# TODO refactor
@app.route('/autofilter/<schema>/<table>', methods=['GET', 'POST'])
def auto_filter(schema, table):
    limit = 200
    dropdowns = {}
    other_cols = {}
    try:
        cur.execute(
            "select column_name  from information_schema.columns where table_schema = '"
            + schema + "' and table_name = '" + table + "'")
        columns = [c[0] for c in cur.fetchall()]
        for c in columns:
            cur.execute(f"select {c} from {table} group by 1 limit {limit + 1}")
            count = -1
            res = cur.fetchall()
            if res is not None:
                count = len(res)
            if c != 'id' and count and limit > count > -1:
                cur.execute(f"select distinct {c} from {table} order by 1 asc")
                vals = cur.fetchall()
                dropdowns[c] = [{'value': '------', 'selected': False}]
                for v in vals:
                    if request.form[c] != '' and request.form[c] == v[0]:
                        dropdowns[c].append({'value': v[0], 'selected': True})
                    else:
                        dropdowns[c].append({'value': v[0], 'selected': False})
            else:
                other_cols[c] = c
        add_str = ''
        extra_params = []
        if len(request.form) > 0:
            for tup in request.form:
                if request.form[tup] != '------' and request.form[tup] != '':
                    extra_params.append(f"{tup} = '{request.form[tup]}'")
            add_str = ' WHERE ' + ' AND '.join(extra_params)
        cur.execute(f"select * from {table} {add_str}")
        rows = cur.fetchmany(500)
    except psycopg2.Error as e:
        return render_template('sql_editor.html', error=e.pgerror)
    return render_template('auto_filter.html',
                           dropdowns=dropdowns,
                           other_cols=other_cols,
                           rows=rows,
                           columns=columns,
                           schema=schema,
                           table=table)


if __name__ == '__main__':
    app.run()
