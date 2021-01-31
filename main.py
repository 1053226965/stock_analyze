from data_fetch import ts_helper
from stock_db import stock_db
import time
import json
import logging

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
      left_stocks.append(stock["ts_code"])
      time.sleep(3)

  while left_stocks:
    code, market = left_stocks[-1].split(".")
    if save_sheet(market, code, req_func, save_func):
      left_stocks.pop()
    else:
      logging.warn("failed to get left stock {} {}".format(market, code))

def main():
  success, stocks = g_ts_helper.get_all_stock()
  if not success:
    logging.error("failed to get all stocks")
    return

  save_sheets(stocks, g_ts_helper.get_profit_statement, g_db.save_profit)
  save_sheets(stocks, g_ts_helper.get_balance_sheet, g_db.save_balance)
  save_sheets(stocks, g_ts_helper.get_cash_flow_sheet, g_db.save_cash_flow)
  save_sheets(stocks, g_ts_helper.get_fina_indicator_sheet, g_db.save_fina_indicator)

if __name__ == "__main__":
  logging.basicConfig(filename="stock.log", level= logging.INFO, format = '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
  main()
