from data_fetch import ts_helper
from stock_db import stock_db
import time
import json
import logging
import helper
from draw_indicator import stock_indicator
from save_file import indicator_store
from helper import ReportedPeriod

g_req_time_gap = 1.5
g_token = "0a6beff7740840989d6df56543a886003c3434e67ed1cbe7b8a3215b"


g_ts_helper = ts_helper(g_token, g_req_time_gap)
g_db = stock_db()


def save_sheet(market, code, req_func, save_func, start_date, end_date, period):
  success, profits =req_func(market, code, start_date, end_date, period)
  if not success:
    return True
  for _, profit in profits.items():
    code, market = profit["ts_code"].split(".")
    end_date = profit["end_date"]
    data = json.dumps(profit)
    if not save_func(market, code, end_date, data):
      pass
  return True

def save_sheets(stocks, req_func, save_func, start_date, end_date, period):
  left_stocks = []

  for _, stock in stocks.items():
    code, market = stock["ts_code"].split(".")
    
    if not save_sheet(market, code, req_func, save_func, start_date, end_date, period):
      logging.info("add {} {} to left_stocks".format(market, code))
      left_stocks.append(stock["ts_code"])
      time.sleep(3)

  while left_stocks:
    code, market = left_stocks[-1].split(".")
    if save_sheet(market, code, req_func, save_func, start_date, end_date, period):
      left_stocks.pop()
    else:
      time.sleep(3)
      logging.warning("failed to get left stock {} {}".format(market, code))

def fetch_and_save(start_date, end_date, period, stocks=None):
  if stocks is None:
    success, stocks = g_ts_helper.get_all_stock()
    if not success:
      logging.error("failed to get all stocks")
      return

    success, cs = g_ts_helper.get_stock_companies("SH")
    for _, c in cs.items():
      code, market = c["ts_code"].split(".")
      g_db.save_stock_company(market, code, json.dumps(c))
    success, cs = g_ts_helper.get_stock_companies("SZ")
    for _, c in cs.items():
      code, market = c["ts_code"].split(".")
      g_db.save_stock_company(market, code, json.dumps(c))

    for _, stock in stocks.items():
      code, market = stock["ts_code"].split(".")
      g_db.save_stocks(market, code, json.dumps(stock))

  print("saved sotcks")

  save_sheets(stocks, g_ts_helper.get_profit_statement, g_db.save_profit, start_date, end_date, period)
  print("saved profit sheets")
  save_sheets(stocks, g_ts_helper.get_balance_sheet, g_db.save_balance, start_date, end_date, period)
  print("saved balance sheets")
  save_sheets(stocks, g_ts_helper.get_cash_flow_sheet, g_db.save_cash_flow, start_date, end_date, period)
  print("saved cash_flow sheets")
  save_sheets(stocks, g_ts_helper.get_fina_indicator_sheet, g_db.save_fina_indicator, start_date, end_date, period)
  print("saved indicator sheets")

def fetch_stock_sheet(market, code, start_year, end_year):
  periods = helper.gen_period(start_year, end_year)
  stocks = {0:{"ts_code": "{0}.{1}".format(code, market)}}
  for period in periods:
    fetch_and_save(None, None, period, stocks)

def get_reasonable_stock():
  success, stocks = g_ts_helper.get_all_stock()
  if not success:
    logging.error("failed to get all stocks")
    return

  stocks = g_db.get_stocks()
  # success, daily_basic = g_ts_helper.ooooooooooooo("20210205")
  # code2basic = {}
  # for _, basic in daily_basic.items():
  #   code, market = basic["ts_code"].split(".")
  #   code2basic["{}{}".format(market, code)] = basic

  fs = indicator_store("filter_company.txt")
  for stock in stocks:
    code, market = stock["ts_code"].split(".")
    indicators = g_db.get_annals_indicator(market, code, "2015", "2020", ReportedPeriod.Annals)
    company = {"code": code, "name": stock["name"]}
    
    c = 0
    o = 0
    e = 0
    
    for indi in indicators.values():
      if indi["roe"] >= 17:
        c += 1
      if indi["netprofit_yoy"] >= 2:
        o += 1
      if indi["or_yoy"] >= 5:
        e += 1
      
    if o == len(indicators) and e == len(indicators):
      #si = stock_indicator(market, code, stock["name"], "2010", "2020")
      #si.show()
      fs.save(company)
      

def main():
  fetch_stock_sheet("SH", "603208", "2010", "2021")
  #fetch_and_save(None, None, "20201231")
  #fetch_and_save(None, None, "20210331")
  #print(g_ts_helper.get_profit_statement("SZ", "002080", None, None, "20210331"))
  #get_reasonable_stock()
  #g_db.fix_profit("SH", "603160", "20171231", "admin_exp", 657170440.91)

if __name__ == "__main__":
  logging.basicConfig(filename="stock.log", level= logging.INFO, format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
  main()
