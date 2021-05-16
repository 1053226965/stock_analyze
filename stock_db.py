import MySQLdb
import logging
import json
import math
import helper
from helper import ReportedPeriod

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

  def _get_annals_date_con(self, start_date, end_date, reportedPeriod=ReportedPeriod.Annals):
    ret = []
    for y in range(int(start_date[0:4]), int(end_date[0:4]) + 1):
      ret.append("end_date = '{}{}'".format(y, reportedPeriod))
    return ret

  def _get_num(self, dic, *args):
    for arg in args:
      if arg not in dic or dic[arg] is None or math.isnan(dic[arg]):
        continue
      return dic[arg]
    return 0


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

    try:
      self._cur.execute("""
        create table companies(
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

  def fix_profit(self, market, code, end_date, field, value):
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as profit from profit_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, end_date, market)
    self._cur.execute(sql)
    for row in self._cur.fetchall():
      profit = json.loads(row[0])
      profit[field] = value
      self.save_profit(market, code, end_date, json.dumps(profit))

  def get_profit_sheet(self, market, code, start_date, end_date, reportedPeriod=ReportedPeriod.Annals):
    dates = self._get_annals_date_con(start_date, end_date, reportedPeriod)
    date_condition = " or ".join(dates)
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as profit from profit_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, date_condition, market)
    self._cur.execute(sql)
    rsp = {}
    for row in self._cur.fetchall():
      profit = json.loads(row[0])
      profit["all_exp"] = helper.fix_num(profit["sell_exp"]) + helper.fix_num(profit["admin_exp"]) + \
        helper.fix_num(profit["fin_exp"])
      rsp[profit["end_date"]] = profit
    return rsp

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

  def get_balance_sheet(self, market, code, start_date, end_date, reportedPeriod=ReportedPeriod.Annals):
    dates = self._get_annals_date_con(start_date, end_date, reportedPeriod)
    date_condition = " or ".join(dates)
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as balance from balance_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, date_condition, market)
    self._cur.execute(sql)
    rsp = {}
    for row in self._cur.fetchall():
      balance = json.loads(row[0])
      balance["weak_ind"] = helper.fix_num(balance["notes_receiv"]) + \
        helper.fix_num(balance["accounts_receiv"]) + helper.fix_num(balance["prepayment"])
      balance["strong_ind"] = helper.fix_num(balance["notes_payable"]) + \
        helper.fix_num(balance["acct_payable"]) + helper.fix_num(balance["adv_receipts"])
      balance["ind_position"] = balance["strong_ind"] / balance["weak_ind"] if  balance["weak_ind"] > 0 else 0
      balance["interest_liab"] = helper.fix_num(balance["st_borr"]) + helper.fix_num(balance["lt_borr"]) + \
        helper.fix_num(balance["bond_payable"]) + helper.fix_num(balance["non_cur_liab_due_1y"]) + \
          helper.fix_num(balance["st_borr"])
      rsp[balance["end_date"]] = balance
    return rsp
  
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

  def get_cash_flow_sheet(self, market, code, start_date, end_date, reportedPeriod=ReportedPeriod.Annals):
    dates = self._get_annals_date_con(start_date, end_date, reportedPeriod)
    date_condition = " or ".join(dates)
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as cash from cash_flow_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, date_condition, market)
    self._cur.execute(sql)
    rsp = {}
    for row in self._cur.fetchall():
      cash = json.loads(row[0])
      
      rsp[cash["end_date"]] = cash
    return rsp

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

  def save_stock_company(self, market, code, json_str):
    json_str = json_str.replace("\\", "\\\\")
    try:
      sql = """
        insert into companies(market, code, json_str) 
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

  def get_stocks(self):
    sql = "select convert(uncompress(json_str) using utf8) from stocks"
    self._cur.execute(sql)
    ret = []
    for row in self._cur.fetchall():
      ret.append(json.loads(row[0]))
    return ret

  def get_annals_indicator(self, market, code, start_date, end_date, reportedPeriod=ReportedPeriod.Annals):
    dates = self._get_annals_date_con(start_date, end_date, reportedPeriod)
    date_condition = " or ".join(dates)
    sql = """
      select convert(uncompress(json_str) using utf8mb4) as indicator from fina_indicator_ss 
      where code = '{}' and ({}) and market = '{}'
      """.format(code, date_condition, market)
    
    balance_rsp = self.get_balance_sheet(market, code, \
       self.add_year(start_date, -1), end_date, reportedPeriod)
    profit_rsp = self.get_profit_sheet(market, code, \
       self.add_year(start_date, -1), end_date, reportedPeriod)
    cash_rsp = self.get_cash_flow_sheet(market, code, \
       self.add_year(start_date, -1), end_date, reportedPeriod)
    
    self._cur.execute(sql)
    ret = {}
    for row in self._cur.fetchall():
      indicator = json.loads(row[0])
      simple_ind = {}
      simple_ind["end_date"] = indicator.get("end_date", "")
      simple_ind["roe"] = self._get_num(indicator, "roe_waa", "roe")
      simple_ind["roe_dt"] = indicator.get("roe_dt", 0.0)
      simple_ind["roa"] = indicator.get("roa", 0.0)
      simple_ind["grossprofit_margin"] = indicator.get("grossprofit_margin", None)
      simple_ind["netprofit_margin"] = indicator.get("netprofit_margin", 0.0)
      simple_ind["assets_turn"] = indicator.get("assets_turn", 0.0)
      simple_ind["profit_to_gr"] = indicator.get("profit_to_gr", 0.0)
      simple_ind["saleexp_to_gr"] = indicator.get("saleexp_to_gr", 0.0)
      simple_ind["adminexp_of_gr"] = indicator.get("adminexp_of_gr", 0.0)
      simple_ind["finaexp_of_gr"] = indicator.get("finaexp_of_gr", 0.0)
      simple_ind["assets_to_eqt"] = indicator.get("assets_to_eqt", 0)
      simple_ind["dp_assets_to_eqt"] = indicator.get("dp_assets_to_eqt", 0)
      simple_ind["op_yoy"] = indicator.get("op_yoy", 0)
      simple_ind["ebt_yoy"] = indicator.get("ebt_yoy", 0)
      simple_ind["tr_yoy"] = indicator.get("tr_yoy", 0)
      simple_ind["or_yoy"] = helper.fix_num(indicator.get("or_yoy", 0))
      simple_ind["netprofit_yoy"] = indicator.get("netprofit_yoy", 0)
      simple_ind["op_of_gr"] = indicator.get("op_of_gr", 0)
      simple_ind["equity_yoy"] = indicator.get("equity_yoy", 0)
      simple_ind["ar_turn"] = indicator.get("ar_turn", 0)
      simple_ind["fa_turn"] = indicator.get("fa_turn", 0)
      simple_ind["debt_to_assets"] = indicator.get("debt_to_assets", 0)

      try:
        balance = balance_rsp[simple_ind["end_date"]]
        profit = profit_rsp[simple_ind["end_date"]]
        cash = cash_rsp[simple_ind["end_date"]]
        simple_ind["all_exp_gr"] = profit["all_exp"] / profit["revenue"]
        simple_ind["pro_asset_rate"] = (helper.fix_num(balance["fix_assets"]) + helper.fix_num(balance["cip"]) + \
          helper.fix_num(balance["const_materials"]) + helper.fix_num(balance["intan_assets"])) / balance["total_liab_hldr_eqy"]
        if (helper.fix_num(balance["fix_assets"]) + helper.fix_num(balance["cip"]) + \
          helper.fix_num(balance["const_materials"]) + helper.fix_num(balance["intan_assets"])) != 0:
          simple_ind["pro_asset_profit"] = profit["operate_profit"] / (helper.fix_num(balance["fix_assets"]) + helper.fix_num(balance["cip"]) + \
            helper.fix_num(balance["const_materials"]) + helper.fix_num(balance["intan_assets"]))
        simple_ind["cash_insecurity"] = (helper.fix_num(balance["st_borr"]) + helper.fix_num(balance["st_bonds_payable"]) \
            + helper.fix_num(balance["non_cur_liab_due_1y"])) / helper.fix_num(cash["end_bal_cash"], 1)
        if helper.fix_num(profit["revenue"]) != 0:
          simple_ind["rec_insecurity"] = helper.fix_num(balance["accounts_receiv"]) * 12 / helper.fix_num(profit["revenue"], 1)
        
        avg_inventories = 0
        this_date = simple_ind["end_date"]
        if self.add_year(this_date, -1) in balance_rsp:
          avg_inventories = (balance_rsp[self.add_year(this_date, -1)]["inventories"] + \
            balance_rsp[this_date]["inventories"]) / 2 if self.add_year(this_date, -1) in balance_rsp and balance_rsp[self.add_year(this_date, -1)]["inventories"] != None\
              else balance_rsp[this_date]["inventories"]
        simple_ind["inv_turn"] = 0
        if avg_inventories != None and avg_inventories != 0 and this_date in profit_rsp and profit_rsp[this_date]["oper_cost"] != None:
          simple_ind["inv_turn"] = profit_rsp[this_date]["oper_cost"] / avg_inventories
      except Exception as e:
        print("compute error: {} {} {} {}".format(e, market, code, simple_ind["end_date"]))
      ret[simple_ind["end_date"]] = simple_ind
    return ret

  def get_company(self, market, code):
    sql = """
      select convert(uncompress(json_str) using utf8) as company from companies 
      where code = '{}' and market = '{}'
      """.format(code, market)
    self._cur.execute(sql)
    row = self._cur.fetchone()
    if row:
      return json.loads(row[0])

  def add_year(self, date, addend):
    return str((int(date[0:4]) + addend)) + date[4:]

if __name__ == "__main__":
  db = stock_db()
  print(db.get_annals_indicator("SZ", "300498", "2010", "2010"))