#初期化処理を書く
from datetime import datetime
import sqlite3
from flask import Flask

app = Flask(__name__)
#app.config.from_mapping(SECRET_KEY="dev")
# app = Flask(__name__, static_url_path='/kajiApp/static')
#app = Flask(__name__, static_url_path='/kajiApp/static', static_folder='static')
import flaskr.main

from flaskr import db
db.create_works_table()
db.create_workList_table()
db.create_nameList_table()
db.create_家事分類区分_table()
db.create_eat_table()
db.create_eat_detail_table()
db.create_life_detail_table()
db.create_payment_table()
db.create_monthly_work_summary_view()
db.create_life_detail_summary_view()

