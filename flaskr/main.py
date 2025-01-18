from flaskr import app
from flask import render_template,request,redirect,url_for
import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

DATABASE ='database.db'

#ページにアクセスした時
@app.route('/')
def index():

    # 今月のレコードを挿入 管理者画面支払い情報のチェック
    insert_current_month_payment_detail()

    # 今月のレコードを挿入 eat食費
    eat_insert_current_month_record_if_not_exists()

    # 今月のレコードを挿入 life生活費
    insert_life_detail_if_not_exists()


    workList = get_works()
    nameList = request.cookies.get('nameList', default=get_names())
    con = sqlite3.connect(DATABASE)
    #昨日と今日の実績
    db_works = con.execute("SELECT id,day,name,work,percent FROM works where day BETWEEN DATE('now', '-1 day') AND DATE('now')  ORDER BY id desc LIMIT 15").fetchall()
    #今月の集計結果
    db_result = con.execute("""
    SELECT works.name, 
       SUM(workList.workNamePoint * (works.percent * 0.01)) AS total_points, 
       CAST(SUM(workList.workNamePoint * (works.percent * 0.01)) / 
            (SELECT SUM(workList.workNamePoint * (works.percent * 0.01)) 
             FROM works 
             JOIN workList ON works.work_id = workList.work_id
             WHERE strftime('%Y-%m', works.day) = strftime('%Y-%m', 'now')) * 100 AS INTEGER) AS percentage 
    FROM works 
    JOIN workList ON works.work_id = workList.work_id 
    WHERE strftime('%Y-%m', works.day) = strftime('%Y-%m', 'now')
    GROUP BY works.name
    ORDER BY total_points DESC;
    """).fetchall()
    ##折れ線グラフ用データ取得
    query = """
    SELECT 
        works.name, 
        works.day, 
        SUM(workList.workNamePoint * (works.percent * 0.01)) AS total_points
    FROM 
        works 
    JOIN 
        workList 
    ON 
        works.work_id = workList.work_id 
    WHERE 
        works.day BETWEEN DATE('now', '-2 month') AND DATE('now')
    GROUP BY 
        works.name, works.day
    ORDER BY 
        works.day, works.name;
    """
    df = pd.read_sql_query(query, con)

    



    # 家事分類区分のデータ取得
    con = sqlite3.connect(DATABASE)
    db_category_result = con.execute("""
        SELECT works.name, 家事分類区分.区分名,
               SUM(workList.workNamePoint * (works.percent * 0.01)) AS total_points
        FROM works 
        JOIN workList ON works.work_id = workList.work_id 
        JOIN 家事分類区分 ON workList.家事分類区分番号 = 家事分類区分.家事分類区分ID
        WHERE strftime('%Y-%m', works.day) = strftime('%Y-%m', 'now')
        GROUP BY works.name, 家事分類区分.区分名
        ORDER BY works.name, 家事分類区分.区分名;
    """).fetchall()
    con.close()

    # 円グラフ用データの準備
    category_data = []
    for row in db_category_result:
        category_data.append({'name': row[0], 'category': row[1], 'total_points': row[2]})


    con.close()
    works = []
    analysisResults = []
    
    for row in db_works:
        works.append({'id': row[0], 'day': row[1], 'name': row[2], 'work': row[3], 'percent': row[4]})
    for row in db_result:
        analysisResults.append({'name': row[0], 'total_points': row[1],'percentage': row[2] })
    
    # 日付を日付型に変換
    df['day'] = pd.to_datetime(df['day'])
    
    # データをピボットテーブルに変換
    pivot_df = df.pivot(index='day', columns='name', values='total_points').fillna(0)
    
    # データをHTMLに渡すための準備
    dates = pivot_df.index.strftime('%Y-%m-%d').tolist()
    data = pivot_df.to_dict(orient='list')
    
    # monthly_work_summary_viewからデータを取得
    con = sqlite3.connect(DATABASE)
    monthly_summary_query = """
    SELECT yyyymm, name, total_points
    FROM monthly_work_summary_view
    ORDER BY yyyymm, name;
    """
    
    monthly_summary_df = pd.read_sql_query(monthly_summary_query, con)
    con.close()

    # 日付を日付型に変換
    monthly_summary_df['yyyymm'] = pd.to_datetime(monthly_summary_df['yyyymm'], format='%Y%m')

    # データをピボットーブルに変換
    monthly_pivot_df = monthly_summary_df.pivot(index='yyyymm', columns='name', values='total_points').fillna(0)

    # データをHTMLに渡すための準備
    monthly_dates = monthly_pivot_df.index.strftime('%Y-%m').tolist()
    monthly_data = monthly_pivot_df.to_dict(orient='list')

    return render_template(
        'index.html',
        works=works,
        workList=workList,
        nameList=nameList,
        analysisResults=analysisResults,
        current_datetime=datetime.now(),
        dates=dates, 
        data=data,
        category_data=category_data,
        monthly_dates=monthly_dates,
        monthly_data=monthly_data
    )


def get_data_from_db(query):
    conn = sqlite3.connect('database.db')
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


@app.route('/option')
def option():
    con = sqlite3.connect(DATABASE)
    db_workList = con.execute('SELECT * FROM workList ORDER BY work_id desc').fetchall()
    con.close()
    workList = []
    for row in db_workList:
        workList.append({'id': row[0], 'workName': row[1], 'workNamePoint': row[2],'家事分類区分番号': row[3]})

    con = sqlite3.connect(DATABASE)
    db_nameList = con.execute('SELECT * FROM nameList ORDER BY name_id desc').fetchall()
    con.close()
    nameList = []
    for row in db_nameList:
        nameList.append({'id': row[0], 'name': row[1]})


    

    return render_template(
        'option.html',
        workList=workList,
        nameList=nameList
        
    )
###################################################################
@app.route('/life')
def life():
    # データベース接続とデータ取得
    conn = sqlite3.connect('database.db')  
    cursor = conn.cursor()
    
    # 明細が存在しない場合、新規作成
    insert_life_detail_if_not_exists()

    cursor.execute("SELECT year, month, rent, water, electricity, gas FROM life_detail ORDER BY yyyymm desc")
    life_details = cursor.fetchall()
    conn.close()

    return render_template(
        'life.html',
        life_details=life_details  # 取得したデータをテンプレートに渡す
    )

def insert_life_detail_if_not_exists():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()

    # 現在の年と月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    formatted_month = str(current_month).zfill(2)

    # 今年の今月の明細が存在するかチェック
    cursor.execute("SELECT COUNT(*) FROM life_detail WHERE year = ? AND month = ?", (current_year, formatted_month))
    count = cursor.fetchone()[0]

    # 明細が存在しない場合、新規作成
    if count == 0:
        cursor.execute(""" 
            INSERT INTO life_detail (year, month, rent, water, electricity, gas, input_time)
            VALUES (?, ?, 0, 0, 0, 0, CURRENT_TIMESTAMP)
        """, (current_year, formatted_month))
        con.commit()  # 変更をデータベースに保存

    con.close()

@app.route('/update_life_details', methods=['POST'])
def update_life_details():
    # 受け取ったデータをリストに格納
    updates = []
    # フォームのキーを動的に取得
    for i in range(1, len(request.form) // 5 + 1):  # 5は年、月、家賃、水道代、電気代、ガス代の数
        if f'year-{i}' in request.form:  # 存在する場合のみ処理
            year = request.form[f'year-{i}']
            month = request.form[f'month-{i}']
            rent = request.form[f'rent-{i}']
            water = request.form[f'water-{i}']
            electricity = request.form[f'electricity-{i}']
            gas = request.form[f'gas-{i}']
            
            updates.append((rent, water, electricity, gas, year, month))

    # データベースの更新
    con = sqlite3.connect(DATABASE)
    for update in updates:
        con.execute(''' 
            UPDATE life_detail
            SET rent = ?, water = ?, electricity = ?, gas = ?
            WHERE year = ? AND month = ?;
        ''', update)
    
    con.commit()
    con.close()
    
    return redirect(url_for('life'))  # 更新後に元のページにリダイレクト

###################################################################
@app.route('/eat')
def eat():
    # 今年の今月のレコードが存在しなければ挿入
    insert_eat_record_if_not_exists()
    
    # 現在の年と月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    formatted_month = str(current_month).zfill(2)  # 月を"00"という書式にする

    if has_eat_details():  # eat_detail が存在するかチェック
        update_eat_amount(current_year, formatted_month)  # 存在する場合のみ update 関数を呼び出す
    
    records = get_eat_records()

    # 各レコードの明細を取得
    details = { (record[0], record[1]): get_eat_detail_records(record[0], record[1]) for record in records }

    return render_template(
        'eat.html',
        records=records,
        details=details  # 明細を渡す
    )


def insert_eat_record_if_not_exists():
    create_eat_table()  # テーブルを作成
    eat_insert_current_month_record_if_not_exists()  # 今月のレコードを挿入



def has_eat_details():
    # SQLite3 を使って eat_detail テーブルのレコード数を確認する
    con = sqlite3.connect('database.db')  # データベスに接続
    cur = con.cursor()  # カーソルを作成

    # SQLクエリでレコー数を取得
    cur.execute("SELECT COUNT(*) FROM eat_detail")
    count = cur.fetchone()[0]  # 結果からレコード数を取得

    con.close()  # データベース接続を閉じる

    return count > 0  # レコードが1件以上ればTrue




# テーブル作成・データ挿入関数
def create_eat_table():
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # テーブルが存在しない場合の作成
    cur.execute("""
        CREATE TABLE IF NOT EXISTS eat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER,
            month TEXT,  -- 月をTEXT型に変更
            amount REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    con.commit()
    con.close()

def eat_insert_current_month_record_if_not_exists():
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # 現在の年と月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    formatted_month = str(current_month)  # 月をそのまま使用（"00"形式を削除）

    # 今年の今月のレコードが存在するか確認
    cur.execute("""
        SELECT 1 FROM eat WHERE year = ? AND month = ?
    """, (current_year, formatted_month))
    
    record_exists = cur.fetchone()

    # レコードが存在しなければ新規作成
    if not record_exists:
        cur.execute("""
            INSERT INTO eat (year, month, amount, description)
            VALUES (?, ?, ?, ?)
        """, (current_year, formatted_month, 0.0, '初期レコード'))

    con.commit()
    con.close()


# テーブルのデータを取得してHTMLに表示する関数
def get_eat_records():
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # `created_at` の降順で12件取得
    cur.execute("""
        SELECT year, month, amount, description, created_at
        FROM eat
        ORDER BY created_at DESC
        LIMIT 12
    """)
    records = cur.fetchall()
    con.close()

    return records


def update_eat_amount(year, month):
    conn = sqlite3.connect('database.db')  # データベース接続
    cursor = conn.cursor()

    # 年と月を条件にして更新
    cursor.execute('''
        UPDATE eat
        SET amount = (
            SELECT COALESCE(SUM(ed.amount), 0)  -- 合計がNULLの場合は0にする
            FROM eat_detail ed
            WHERE ed.year = eat.year AND ed.month = eat.month
        )
    ''')

    conn.commit()  # 変更をコミット
    conn.close()   # 接続を閉じる

# 新しい関数を追加
def get_eat_detail_records(year, month):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("""
        SELECT id, amount, input_time  
        FROM eat_detail
        WHERE year = ? AND month = ?
    """, (year, month))
    records = cur.fetchall()
    con.close()
    return records



@app.route('/update_detail', methods=['POST'])
def update_detail():
    detail_id = request.form['id']
    amount = request.form['amount']

    con = sqlite3.connect(DATABASE)
    con.execute("""
        UPDATE eat_detail
        SET amount = ?
        WHERE id = ?
    """, (amount, detail_id))
    
    con.commit()
    con.close()
    
    return redirect(url_for('eat'))  # 食費記録ペーにリダイレクト


    

#食費明細
@app.route('/save_detail', methods=['POST'])
def save_detail():
    year = request.form['year']
    month = request.form['month']
    amount = request.form['amount']

    con = sqlite3.connect(DATABASE)
    con.execute("""
        INSERT INTO eat_detail (year, month, amount)
        VALUES (?, ?, ?)
    """, (year, month, amount))
    
    con.commit()
    con.close()
    
    return redirect(url_for('eat'))  # 食費記録ページにリダイレクト

##################################################################
@app.route('/admin')
def admin():
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    # 現在の年と月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month

    # 今月の payment 明細が存在しない場合、新規作成
    insert_current_month_payment_detail()

    # ここでビューを使用してデータを取得
    cur.execute("""
                SELECT * 
                FROM life_detail_summary 
                JOIN payment ON life_detail_summary.yyyymm = payment.yyyymm
                WHERE payment.決裁 <> "済" 
                OR payment.決裁 is null
                ORDER BY yyyymm asc ;
                
        """)
    records = cur.fetchall()

    # 名前リストの取得
    cur.execute("SELECT name_id, name FROM nameList ORDER BY name_id DESC")
    nameList = cur.fetchall()

    # 明細の取得
    cur.execute(""" 
        SELECT payment.yyyymm, nameList.name, payment.pay, payment.決裁 
        FROM payment
        JOIN nameList ON payment.name_code = nameList.name_id
        --JOIN life_detail_summary ON payment.yyyymm = life_detail_summary.yyyymm
        WHERE payment.決裁 <> "済" 
                OR payment.決裁 is null
        --OR life_detail_summary.支払い完了="過払"
        ORDER BY payment.yyyymm asc;
    """)
    payment_details = cur.fetchall()

    con.close()
    return render_template('admin.html', records=records, nameList=nameList, payment_details=payment_details)

def insert_current_month_payment_detail():
    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()

    # 現在の年と月を取得
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    formatted_month = str(current_month).zfill(2)

    # 今年の今月の payment 明細が存在するかチェック
    yyyymm = f"{current_year}{formatted_month}"  # 年と月を結合してyyyymmを作成
    cursor.execute("SELECT COUNT(*) FROM payment WHERE yyyymm = ?", (yyyymm,))
    count = cursor.fetchone()[0]

    # 明細が存在しない場合、新規作成
    if count == 0:
        cursor.execute(""" 
            INSERT INTO payment (year, month, pay, name_code)
            VALUES (?, ?, 0, ?) 
        """, (current_year, formatted_month, 1))  # name_codeは適切な値に変更してください
        con.commit()  # 変更をデータベースに保存

    con.close()

@app.route('/update_payment', methods=['POST'])
def update_payment():
    yyyymm = request.form['yyyymm']  # 年月を取得
    pay = request.form['pay']  # 支払金額を取得

    print(f"Updating payment: yyyymm={yyyymm}, pay={pay}")  # デバッグ用ログ

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # paymentテーブルの更新
    cur.execute(""" 
        UPDATE payment
        SET pay = ?
        WHERE yyyymm = ?;  
    """, (pay, yyyymm))
    
    con.commit()  # 変更をコミット
    con.close()  # 接続を閉じる
    
    return redirect(url_for('admin'))  # 更新後に管理者画面にリダイレクト


@app.route('/update_settlement', methods=['POST'])
def update_settlement():
    yyyymm = request.form['yyyymm']  # 年月を取得
    settlement = request.form['settlement']  # 決裁金額を取得

    print(f"Updating settlement: yyyymm={yyyymm}, settlement={settlement}")  # デバッグ用ログ

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # paymentテーブルの更新
    cur.execute(""" 
        UPDATE payment
        SET 決裁 = ?
        WHERE yyyymm = ?;  
    """, (settlement, yyyymm))
    
    con.commit()  # 変更をコミット
    con.close()  # 接続を閉じる
    
    return redirect(url_for('admin'))  # 更新後に管理者画面にリダイレクト



##################################################################
#家事実績テーブル
@app.route('/register',methods=['post'])
def register():

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute('SELECT MAX(id) FROM works')
    max_id = cursor.fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1
    con.close()
    id = new_id
    day = request.form['day']
    name = request.form['name']
    work_id = request.form['workId']
    work = request.form['workName']
    percent = request.form['percent']

    con = sqlite3.connect(DATABASE)
    con.execute('INSERT INTO works VALUES(?,?,?,?,?,?)',
               [id,day,name,work_id,work,percent] )
    
    con.commit()
    con.close()
    response = redirect(url_for('index'))
    response.set_cookie('name', name, max_age=31536000)  # 1年の有効期間
    return response


#家事リストの挿入
@app.route('/register2',methods=['post'])
def register2():

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute('SELECT MAX(work_id) FROM workList')
    max_id = cursor.fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1

    con.close()
    work_id=new_id
    workName=request.form['workName']
    workNamePoint=request.form['workNamePoint']
    家事分類区分番号=request.form['家事分類区分番号']
    con = sqlite3.connect(DATABASE)
    con.execute('INSERT INTO workList VALUES(?,?,?,?)',
               [work_id,workName,workNamePoint,家事分類区分番号] )
    
    con.commit()
    con.close()
    return redirect(url_for('option'))


#名前リストの挿入
@app.route('/register3',methods=['post'])
def register3():

    con = sqlite3.connect(DATABASE)
    cursor = con.cursor()
    cursor.execute('SELECT MAX(name_id) FROM nameList')
    max_id = cursor.fetchone()[0]
    if max_id is None:
        new_id = 1
    else:
        new_id = max_id + 1
    con.close()
    name_id=new_id
    name=request.form['name']
    con = sqlite3.connect(DATABASE)
    con.execute('INSERT INTO nameList VALUES(?,?)',
               [name_id,name] )
    con.commit()
    con.close()
    return redirect(url_for('option'))






def get_works():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT work_id, workName,workNamePoint,家事分類区分番号 FROM workList")
    works = cursor.fetchall()
    conn.close()
    return [(work[0], work[1],work[2],work[3]) for work in works]

def get_names():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM nameList")
    names = cursor.fetchall()
    conn.close()
    
    return [name[0] for name in names]





if __name__ == '__main__' :
    app.run(debug=True ,host='0.0.0.0',port=8888)
    #app.run(debug=False ,host='100.64.16.21',port=80)










