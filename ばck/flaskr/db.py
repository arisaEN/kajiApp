import sqlite3
DATABASE='database.db'
#明細
def create_works_table():
    con=sqlite3.connect('database.db')
    con.execute("CREATE TABLE IF NOT EXISTS works(id INTEGER PRIMARY KEY AUTOINCREMENT, day date, name TEXT,work_id INTEGER, work TEXT, percent TEXT)")

    con.close()

#家事リスト
def create_workList_table():
    con=sqlite3.connect('database.db')
    con.execute("CREATE TABLE IF NOT EXISTS workList(work_id INTEGER PRIMARY KEY AUTOINCREMENT, workName text, workNamePoint text,家事分類区分番号 INTEGER)")

    con.close()
#オペレーター名前リスト
def create_nameList_table():
    con=sqlite3.connect('database.db')
    con.execute("CREATE TABLE IF NOT EXISTS nameList(name_id INTEGER PRIMARY KEY AUTOINCREMENT, name text)")

    con.close()

#家事分類区分
def create_家事分類区分_table():
    con=sqlite3.connect('database.db')
    con.execute("CREATE TABLE IF NOT EXISTS 家事分類区分(家事分類区分番号ID INTEGER PRIMARY KEY AUTOINCREMENT, 区分番号 INTEGER, 区分名 varchar(40))")

    con.close()

#食費入力用
def create_eat_table():
    con=sqlite3.connect('database.db')
    con.execute("CREATE TABLE IF NOT EXISTS eat (id INTEGER PRIMARY KEY AUTOINCREMENT,year TEXT,month TEXT,amount INTEGER,description TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")  # 修正箇所

    con.close()
#食費明細
def create_eat_detail_table():
    con = sqlite3.connect('database.db')
    con.execute("""
        CREATE TABLE IF NOT EXISTS eat_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT,
            month TEXT,
            amount INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            yyyymm TEXT GENERATED ALWAYS AS (
                year || 
                CASE 
                    WHEN LENGTH(month) = 1 THEN '0' || month 
                    ELSE month 
                END
            ) VIRTUAL
        );
    """)
    con.close()  

#生活費
def create_life_detail_table():
    con = sqlite3.connect('database.db')
    con.execute("""
        CREATE TABLE IF NOT EXISTS life_detail (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT,
            month TEXT,
            rent INTEGER,
            water INTEGER,
            electricity INTEGER,
            gas INTEGER,
            input_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            yyyymm TEXT GENERATED ALWAYS AS (
                year || 
                CASE 
                    WHEN LENGTH(month) = 1 THEN '0' || month 
                    ELSE month 
                END
            ) VIRTUAL
        );
    """) 
    con.close()  


def create_payment_table():
    con = sqlite3.connect('database.db')
    con.execute("""
        CREATE TABLE IF NOT EXISTS "payment" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT,
            "year" TEXT,
            "month" TEXT,
            "name_code" INTEGER,
            "pay" INTEGER,
            "input_time" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            "yyyymm" TEXT GENERATED ALWAYS AS (
                "year" || 
                CASE 
                    WHEN LENGTH("month") = 1 THEN '0' || "month" 
                    ELSE "month" 
                END
            ) VIRTUAL
        );
    """)
    con.close()

def create_monthly_work_summary_view():
    con = sqlite3.connect('database.db')
    con.execute("""
        CREATE VIEW IF NOT EXISTS monthly_work_summary_view AS
        SELECT strftime('%Y%m', w.day) AS yyyymm,
               w.name, 
               SUM(workList.workNamePoint * (w.percent * 0.01)) AS total_points, 
               CAST(SUM(workList.workNamePoint * (w.percent * 0.01)) / 
                    (SELECT SUM(workList.workNamePoint * (w.percent * 0.01)) 
                     FROM works w2
                     JOIN workList ON w2.work_id = workList.work_id
                     WHERE strftime('%Y%m', w2.day) = strftime('%Y%m', w.day)) * 100 AS INTEGER) AS percentage
        FROM works w
        JOIN workList ON w.work_id = workList.work_id 
        GROUP BY w.name, strftime('%Y%m', w.day)
        ORDER BY yyyymm DESC;
    """)
    con.commit()
    con.close()


def create_life_detail_summary_view():
    con = sqlite3.connect('database.db')
    con.execute("""
        CREATE VIEW IF NOT EXISTS life_detail_summary AS
    SELECT * FROM (
    SELECT 
        COALESCE(e.yyyymm, l.yyyymm) AS yyyymm, 
        printf('¥%,d', e.amount) AS 食費, 
        printf('¥%,d', l.rent) AS 家賃, 
        printf('¥%,d', l.water) AS 水道代, 
        printf('¥%,d', l.electricity) AS 電気代, 
        printf('¥%,d', l.gas) AS ガス代, 
        printf('¥%,d', (l.rent + l.water + l.electricity + l.gas)) AS 生活費合計, 
        printf('¥%,d', (COALESCE(e.amount, 0) + l.rent + l.water + l.electricity + l.gas)) AS 生活費_食費, 
        printf('¥%,d', (COALESCE(e.amount, 0) + l.rent + l.water + l.electricity + l.gas) / 2) AS 折半計算,
        -- 家事割合適用後の折半代金を計算
        FLOOR( (((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) 
            - FLOOR( (((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) * 0.25 * COALESCE(m.percentage, 0) / 100 ) 
            ) AS 家事割合適用後折半代金,
        m.percentage AS "荻田%",
        printf('¥%,d', COALESCE(p.pay, 0)) AS 支払金額,  -- 支払金額をフォーマット
        nl.name AS 支払人,
        -- 支払い完了の判定
        CASE 
            WHEN COALESCE(p.pay, 0) > FLOOR( (((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) 
                - FLOOR((((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) * 0.25 * COALESCE(m.percentage, 0) / 100) )
            THEN '過払'
            WHEN COALESCE(p.pay, 0) = FLOOR( (((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) 
                - FLOOR((((l.rent + l.water + l.electricity + l.gas + e.amount) / 2) - e.amount) * 0.25 * COALESCE(m.percentage, 0) / 100) )
            THEN '済' 
            ELSE '未' 
        END AS 支払い完了
    FROM 
        life_detail l
    LEFT JOIN 
        eat e 
    ON 
        e.yyyymm = l.yyyymm
    LEFT JOIN 
        monthly_work_summary_view m 
    ON 
        l.yyyymm = m.yyyymm 
        AND m.name = '荻田'
    LEFT JOIN 
        payment p 
    ON 
        l.yyyymm = p.yyyymm
    LEFT JOIN 
        nameList nl 
    ON 
        p.name_code = nl.name_id
    ) AS temp
    ORDER BY 
    CASE 
        WHEN 支払い完了 = '未' THEN 0 
        WHEN 支払い完了 = '過払' THEN 1 
        ELSE 2 
    END, 
    yyyymm;
    """)
    con.commit()
    con.close()
    

