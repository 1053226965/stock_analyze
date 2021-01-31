import MySQLdb
import logging
import json

g_mysql_config = {
  "host": "127.0.0.1",
  "port": 3306,
  "user": "root",
  "passwd": "pzc123",
  "charset": "utf8mb4"
}

class stock_db:
  def __init__(self):
    self._db = MySQLdb.connect(**g_mysql_config)
    self._cur = self._db.cursor()
    self._insert_counter = 0
    self.prepare()

    # self._cur.execute("drop table test")
    # self._cur.execute("""
    #     create table test(
    #       market blob
    #     )
    #     """)
    # print(json.dumps({'ss':'你好'}))
    # print(json.loads(""" {"ss": "\u4f60\u597d"} """))
    # self._cur.execute(r"""
    #   insert into test values(compress('\u4e3b\u677f'))
    #   """)
    # self._cur.execute("""
    #   select convert(uncompress(market) using utf8) from test
    #   """)
    # print(self._cur.fetchone()[0])
    # exit(0)

  def __del__(self):
    self._db.commit()
    self._db.close()

  def _try_commit(self):
    self._insert_counter += 1
    if self._insert_counter >= 300:
      self._db.commit()
      self._insert_counter = 0

  def _get_annals_date_con(self, start_date, end_date):
    ret = []
    for y in range(int(start_date[0:4]), int(end_date[0:4]) + 1):
      ret.append("end_date = '{}1231'".format(y))
    return ret

  def prepare(self):
    try:
      self._cur.execute("create database stock")
    except MySQLdb.Error as _:
      pass

    self._cur.execute("use stock")

    try:
      self._cur.execute("""
        create table stocks(
          market varchar(16),
          code varchar(16),
          json_str blob,
          primary key(code, market)
        )
        """)
    except MySQLdb.Error as _:
      pass

    tables = ["profit_ss", "balance_ss", "cash_flow_ss", "fina_indicator_ss"]
    for table_name in tables:
      try:
        self._cur.execute("""
          create table {}(
            market varchar(16),
            code varchar(16),
            end_date varchar(8),
            json_str blob,
            primary key(code, end_date, market)
          )
          """.format(table_name))
      except MySQLdb.Error as _:
        pass
    self._db.commit()

  def save_stocks(self, market, code, json_str):
    json_str = json_str.replace("\\", "\\\\")
    try:
      sql = """
        insert into stocks(market, code, json_str) 
        values('{}', '{}', compress('{}'))
        """.format(market, code, json_str)
      self._cur.execute(sql)
      self._try_commit()
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
      return False

  def save_profit(self, market, code, end_date, json_str):
    try:
      sql = """
        insert into profit_ss(market, code, end_date, json_str) 
        values('{}', '{}', '{}', compress('{}'))
        """.format(market, code, end_date, json_str)
      self._cur.execute(sql)
      self._try_commit()
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
      self._try_commit()
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
      self._try_commit()
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
      self._try_commit()
      return True
    except MySQLdb.Error as e:
      if self._db.errno() != 1062:
        logging.error("{}".format(e))
        exit(-1)
    return False

  def get_stocks(self):
    sql = "select convert(uncompress(json_str) using utf8) from stocks"
    self._cur.execute(sql)
    ret = []
    for row in self._cur.fetchall():
      ret.append(json.loads(row[0]))
    return ret

  def get_annals_indicator(self, market, code, start_date, end_date):
    dates = self._get_annals_date_con(start_date, end_date)
    date_condition = " or ".join(dates)
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as indicator from fina_indicator_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, date_condition, market)
    
    self._cur.execute(sql)
    ret = []
    for row in self._cur.fetchall():
      indicator = json.loads(row[0])
      simple_ind = {}
      simple_ind["end_date"] = indicator.get("end_date", "")
      simple_ind["roe"] = indicator.get("roe_waa", 0.0)
      simple_ind["roe_dt"] = indicator.get("roe_dt", 0.0)
      simple_ind["grossprofit_margin"] = indicator.get("grossprofit_margin", 0.0)
      simple_ind["netprofit_margin"] = indicator.get("netprofit_margin", 0.0)
      simple_ind["assets_turn"] = indicator.get("assets_turn", 0.0)
      simple_ind["profit_to_gr"] = indicator.get("profit_to_gr", 0.0)
      simple_ind["saleexp_to_gr"] = indicator.get("saleexp_to_gr", 0.0)
      simple_ind["adminexp_of_gr"] = indicator.get("adminexp_of_gr", 0.0)
      simple_ind["finaexp_of_gr"] = indicator.get("finaexp_of_gr", 0.0)
      simple_ind["assets_to_eqt"] = indicator.get("assets_to_eqt", 0)
      ret.append(simple_ind)
    return sorted(ret, key=lambda item: item["end_date"])

if __name__ == "__main__":
  db = stock_db()
  db.get_annals_indicator("SH", "600480", "20191231", "20191231")