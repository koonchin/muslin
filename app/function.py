import datetime
import mysql.connector
import requests

hostdb = '139.162.28.194'

passworddb = 'Chino002'

databasedb = 'ecommerce'

userdb = 'gink'


class DB:
    mydb = None

    def connect(self, dbname=databasedb):
        self.mydb = mysql.connector.connect(
            host=hostdb,
            user=userdb,
            password=passworddb,
            database=dbname,
            port='3306'
        )

    def query_with_image(self, query, args):
        self.connect()
        cursor = self.mydb.cursor(buffered=True)
        result = cursor.execute(query, args)
        self.mydb.commit()

    def query(self, task):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except Exception as E:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        return mycursor

    def check(self, task, db='muslin'):
        try:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except Exception as E:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)

        return mycursor.fetchall()

    def query_custom(self, task, db):
        try:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
        except Exception as E:
            self.connect(dbname=db)
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)

        return mycursor

    def query_commit(self, task):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            self.mydb.commit()
        except Exception as E:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.execute(task)
            self.mydb.commit()
        return mycursor

    def query_commit_many(self, task, rows):
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.executemany(task, rows)
            self.mydb.commit()
        except Exception as E:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.executemany(task, rows)
            self.mydb.commit()
        return mycursor

    def callproc(self, procname: str, task_db, task_db2):
        arg = [task_db, task_db2]
        try:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.callproc(procname, arg)
            self.mydb.commit()
        except Exception as E:
            self.connect()
            mycursor = self.mydb.cursor(buffered=True)
            mycursor.callproc(procname, arg)
            self.mydb.commit()

    def create_table(self, dbname):
        task = f'''create table if not exists {dbname} (  `sku` longtext NOT NULL,
                    `descript` longtext,
                    `amount` int DEFAULT NULL )'''
        db.query_commit(task)

    def insert_into_duplicate(self, dbname, data, amount):
        task = f"""
        INSERT INTO {dbname}(sku, descript, amount)
        VALUES ({data})
        ON DUPLICATE KEY UPDATE amount = {amount};  
        """
        # db.query_commit(task)


class Web():
    def __init__(self, apikey, apisecret, storename) -> None:
        self.apikey = apikey
        self.apisecret = apisecret
        self.storename = storename

    #  upload trackingno today to database
    def post_order(self, data):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "ADDORDER", 'version': '3'}

        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(res.status_code)

    def update_order_status(self, number):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "UPDATEORDERSTATUS",
                   'version': '3', 'number': number, 'status': 1}

        res = requests.post(url=url, headers=header, params=payload)
        print(number, res.status_code)

    def post_purchase_order(self, data):
        header = {
            'storename': f'{self.storename}',
            'apikey': f'{self.apikey}',
            'apisecret': f'{self.apisecret}'
        }

        url = 'https://api.zortout.com/api.aspx'

        payload = {'method': "ADDPURCHASEORDER", 'version': '3'}

        res = requests.post(url=url, headers=header, params=payload, json=data)
        print(res.status_code)


db = DB()
web = Web("7KRzYzjPqknzzSM2nVcooo3sWNF6EK4Oyq9QtGI8uyk=",
          "RA9VD1AjwaHo8UW0uNk924SnxN0xIFIGdlelDEcTEE=", "Muslin.info@gmail.com")
