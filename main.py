from data_fetch import ts_helper
from stock_db import stock_db
import time
import json
import logging
from draw_indicator import stock_indicator

g_req_time_gap = 1.5
g_token = "0a6beff7740840989d6df56543a886003c3434e67ed1cbe7b8a3215b"


g_ts_helper = ts_helper(g_token, g_req_time_gap)
g_db = stock_db()


def save_sheet(market, code, req_func, save_func):
  success, profits =req_func(market, code, "20000101", "20301231")
  if not success:
    return False
  for _, profit in profits.items():
    code, market = profit["ts_code"].split(".")
    end_date = profit["end_date"]
    data = json.dumps(profit)
    if not save_func(market, code, end_date, data):
      pass
  return True

def save_sheets(stocks, req_func, save_func):
  left_stocks = []

  for _, stock in stocks.items():
    code, market = stock["ts_code"].split(".")
    
    if not save_sheet(market, code, req_func, save_func):
      logging.info("add {} {} to left_stocks".format(market, code))
      left_stocks.append(stock["ts_code"])
      time.sleep(3)

  while left_stocks:
    code, market = left_stocks[-1].split(".")
    if save_sheet(market, code, req_func, save_func):
      left_stocks.pop()
    else:
      time.sleep(3)
      logging.warning("failed to get left stock {} {}".format(market, code))

def fetch_and_save():
  success, stocks = g_ts_helper.get_all_stock()
  if not success:
    logging.error("failed to get all stocks")
    return

  for _, stock in stocks.items():
    code, market = stock["ts_code"].split(".")
    g_db.save_stocks(market, code, json.dumps(stock))
  exit(0)
  print("saved sotcks")

  save_sheets(stocks, g_ts_helper.get_profit_statement, g_db.save_profit)
  print("saved profit sheets")
  save_sheets(stocks, g_ts_helper.get_balance_sheet, g_db.save_balance)
  print("saved balance sheets")
  save_sheets(stocks, g_ts_helper.get_cash_flow_sheet, g_db.save_cash_flow)
  print("saved cash_flow sheets")
  save_sheets(stocks, g_ts_helper.get_fina_indicator_sheet, g_db.save_fina_indicator)
  print("saved indicator sheets")

def get_reasonable_stock():
  success, stocks = g_ts_helper.get_all_stock()
  if not success:
    logging.error("failed to get all stocks")
    return

  stocks = g_db.get_stocks()
  for stock in stocks:
    code, market = stock["ts_code"].split(".")
    indicators = g_db.get_annals_indicator(market, code, "2010", "2020")
    
    c = 0
    for indi in indicators:
      if indi["roe"] >= 20:
        c += 1
    if c > 5:
      si = stock_indicator(market, code, stock["name"], "2010", "2020")
      si.show()

def main():
  get_reasonable_stock()

if __name__ == "__main__":
  logging.basicConfig(filename="stock.log", level= logging.INFO, format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
  main()
