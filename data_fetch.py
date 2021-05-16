import tushare as ts
import time
import numpy

class ts_helper:
  def __init__(self, token, req_time_gap):
    self._pro = ts.pro_api(token)
    self._last_time = 0
    self._req_time_gap = req_time_gap

  def _flow_control(self):
    now = time.time()
    dif = now - self._last_time
    if dif < self._req_time_gap:
      time.sleep(self._req_time_gap - dif)
    self._last_time = now

  def _format(self, rsp):
    ts_codes = rsp["ts_code"]
    ret = {}
    for key, value in rsp.items():
      for i, _ in ts_codes.items():
        if i not in ret:
          ret[i] = {}
        v = value[i]
        if isinstance(v, numpy.int64):
          v = int(v)
        ret[i][key] = v
    return ret

  def get_all_stock(self):
    self._flow_control()
    try:
      rsp = self._pro.stock_basic(exchange='', list_status='L')
    except:
      return False, None
    return True, self._format(rsp)

  def get_profit_statement(self, market, code, start_date, end_date, period=None):
    self._flow_control()
    try:
      rsp = self._pro.income(ts_code="{}.{}".format(code, market), start_date=start_date,\
        end_date=end_date, period=period)
    except:
      return False, None
    return True, self._format(rsp)

  def get_balance_sheet(self, market, code, start_date, end_date, period=None):
    self._flow_control()
    try:
      rsp = self._pro.balancesheet(ts_code="{}.{}".format(code, market), start_date=start_date,\
        end_date=end_date, period=period)
    except:
      return False, None
    return True, self._format(rsp)

  def get_cash_flow_sheet(self, market, code, start_date, end_date, period=None):
    self._flow_control()
    try:
      rsp = self._pro.cashflow(ts_code="{}.{}".format(code, market), start_date=start_date,\
        end_date=end_date, period=period)
    except:
      return False, None
    return True, self._format(rsp)

  def get_fina_indicator_sheet(self, market, code, start_date, end_date, period=None):
    self._flow_control()
    try:
      rsp = self._pro.fina_indicator(ts_code="{}.{}".format(code, market), start_date=start_date,\
        end_date=end_date, period=period)
    except:
      return False, None
    return True, self._format(rsp)

  def get_daily_basic(self, trade_date=None, market=None, code=None):
    self._flow_control()
    try:
      rsp = self._pro.daily_basic(ts_code="{}.{}".format(code, market) if market and code else "", \
        trade_date=trade_date)
    except Exception as e:
      print("{}".format(e))
      return False, None
    return True, self._format(rsp)

  def get_stock_companies(self, market):
    self._flow_control()
    try:
      rsp = self._pro.stock_company(exchange="SSE" if market == "SH" else "SZSE")
    except:
      return False, None
    return True, self._format(rsp)