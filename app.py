import json
from datetime import date
from flask import Flask, render_template, request

import pymysql

app = Flask(__name__)


class DAL:
    def __init__(self, conf, dsql):
        self.host = conf["host"]
        self.port = conf["port"]
        self.user = conf["user"]
        self.password = conf["password"]
        self.database = conf["database"]
        self.con = None
        self.dsql = dsql

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        self.con = pymysql.connect(host=self.host,
                                   user=self.user,
                                   password=self.password,
                                   database=self.database,
                                   port=self.port)

    def close(self):
        if self.con:
            self.con.close()
        self.con = None

    def getData(self, ind: str):
        sql = self.dsql[ind]
        cur = self.con.cursor()
        print(sql)
        cur.execute(sql)
        rows = cur.fetchall()

        return rows


with open("config.json", encoding='utf-8') as json_data_file:
    data = json.load(json_data_file)
    autorefresh = data["autorefresh"]
    timing = data["timing"]



@app.route('/')
def report():
    headings: dict = {}
    datarows: dict = {}
    curdate = date.today().strftime("%d/%m/%Y")

    headings["sql1"] = ('Назва', 'Кількість')
    headings["sql2"] = ('Назва групи', 'Кількість')
    headings["sql3"] = ('ФІО', 'Кількість')

    print(f"Поточна дата: {curdate}")

    with DAL(data["mysql"], data["queries"]) as dal:
        for i in range(1, 4):
            key = f"sql{i}"
            datarows[key] = dal.getData(key)

    return render_template('report.html', headings=headings, data=datarows, autorefresh=autorefresh, timing=timing,
                           curdate=curdate)


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="0.0.0.0", port=5001)
