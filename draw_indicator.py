import matplotlib.pyplot as plt
import sheet_prompt
from stock_db import stock_db

class stock_indicator:

  def __init__(self, market, code, start_date, end_date):
    self._db = stock_db()
    self._market = market
    self._code = code
    self._start_date = start_date
    self._end_date = end_date

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

  def _import_data_polyline(self, rsp, indi_name, prompt):
    x = []
    y = []
    for indi in rsp:
      y.append(indi.get(indi_name, 0))
      x.append(indi["end_date"][0:4])
    for a, b in zip(x, y):
      plt.text(a, b + 0.3, b, ha='center', va='bottom', fontsize=8)
    plt.plot(x, y, label=prompt)

  def _import_data_bar(self, rsp, indi_name, prompt):
    x = []
    y = []
    for indi in rsp:
      y.append(indi.get(indi_name, 0))
      x.append(indi["end_date"][0:4])
    for a, b in zip(x, y):
      plt.text(a, b + 0.3, b, ha='center', va='bottom', fontsize=8)
    plt.bar(x, y, label=prompt)

    
  def show(self):
    rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)

    fig = plt.figure(figsize=(8, 6))
    fig.canvas.set_window_title("{} {}".format(self._market, self._code))

    plt.subplot(3, 3, 1)
    self._import_data_polyline(rsp, "roe", "roe")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 3, 2)
    self._import_data_polyline(rsp, "grossprofit_margin", "毛利率")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 3, 3)
    self._import_data_polyline(rsp, "profit_to_gr", "净利率")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 3, 4)
    self._import_data_polyline(rsp, "saleexp_to_gr", "销售费用占比")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 3, 5)
    self._import_data_polyline(rsp, "adminexp_of_gr", "管理费用占比")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 3, 6)
    self._import_data_polyline(rsp, "finaexp_of_gr", "财务费用占比")
    plt.legend()
    plt.ylabel("%")

    plt.subplot(3, 2, 5)
    self._import_data_bar(rsp, "assets_to_eqt", "权益乘数")
    plt.legend()
    plt.ylim([0, 10])

    plt.subplot(3, 2, 6)
    self._import_data_bar(rsp, "assets_turn", "总资产周转率")
    plt.legend()
    plt.ylim([0, 5])

    plt.show()

if __name__ == "__main__":
  s = stock_indicator("SZ", "002127", "2010", "2020")
  s.show()