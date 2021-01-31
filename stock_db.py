import MySQLdb
import logging

g_mysql_config = {
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "passwd": "pzc123"
}

class stock_db:
  def __init__(self):
    self._db = MySQLdb.connect(**g_mysql_config)
    self._cur = self._db.cursor()
    self.prepare()

  def prepare(self):
    try:
      self._cur.execute("create database stock")
    except MySQLdb.Error as _:
      pass

    self._cur.execute("use stock")

    tables = ["profit_ss", "balance_ss", "cash_flow_ss", "fina_indicator_ss"]
    for table_name in tables:
      try:
        self._cur.execute("""
          create table {}(
            market varchar(16),
            code varchar(16),
            end_date varchar(8),
            json_str blob,
            primary key(market, code, end_date)
          )
          """.format(table_name))
      except MySQLdb.Error as _:
        pass
    self._db.commit()

  def save_profit(self, market, code, end_date, json_str):
    try:
      sql = """
        insert into profit_ss(market, code, end_date, json_str) 
        values('{}', '{}', '{}', compress('{}'))
        """.format(market, code, end_date, json_str)
      self._cur.execute(sql)
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
      return False

  def save_balance(self, market, code, end_date, json_str):
    try:
      sql = """
        insert into balance_ss(market, code, end_date, json_str) 
        values('{}', '{}', '{}', compress('{}'))
        """.format(market, code, end_date, json_str)
      self._cur.execute(sql)
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
      return False
  
  def save_cash_flow(self, market, code, end_date, json_str):
    try:
      sql = """
        insert into cash_flow_ss(market, code, end_date, json_str) 
        values('{}', '{}', '{}', compress('{}'))
        """.format(market, code, end_date, json_str)
      self._cur.execute(sql)
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
      return False

  def save_fina_indicator(self, market, code, end_date, json_str):
    try:
      sql = """
        insert into fina_indicator_ss(market, code, end_date, json_str) 
        values('{}', '{}', '{}', compress('{}'))
        """.format(market, code, end_date, json_str)
      self._cur.execute(sql)
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
    return False

  def __del__(self):
    self._db.commit()
    self._db.close()

