import matplotlib.pyplot as plt
import sheet_prompt
from stock_db import stock_db
import math
import threading
import helper

class stock_indicator:

  def __init__(self, market, code, name, start_date, end_date):
    self._db = stock_db()
    self._market = market
    self._code = code
    self._name = name
    self._start_date = start_date
    self._end_date = end_date

    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

  def _import_data_polyline(self, rsp, indi_name, prompt):
    x = []
    y = []
    for indi in rsp:
      y.append(round(indi.get(indi_name, 0), 2))
      x.append(indi["end_date"][0:4])
    for a, b in zip(x, y):
      plt.text(a, b, b, color = "r", ha='center', va='bottom', fontsize=8)
    plt.plot(x, y, label=prompt)

  def _import_data_bar(self, rsp, indi_name, prompt):
    x = []
    y = []
    min_v = 0x7fffffff
    max_v = -0x7fffffff
    for indi in rsp:
      min_v = min(min_v, round(indi.get(indi_name, 0) or 0, 2))
      max_v = max(max_v, round(indi.get(indi_name, 0) or 0, 2))
      y.append(round(indi.get(indi_name, 0) or 0, 2))
      x.append(indi["end_date"][0:4])
    
    ylabel = ""
    if min_v / 10000 > 10 and max_v / 10000 > 10:
      y = [int(helper.fix_num(y[i]) / 10000 + 0.5) for i in range(len(y))]
      min_v = min_v / 10000
      max_v = max_v / 10000
      ylabel = "万"
    for a, b in zip(x, y):
      plt.text(a, b + 0.3, b, color = "r", ha='center', va='bottom', fontsize=8)
      
    plt.bar(x, y, label=prompt)
    plt.ylabel(ylabel)
    min_v = min(0, min_v)
    max_v = max_v * 1.2
    if min_v == max_v:
      max_v += 1
    return min_v, max_v


  def key_press(self, event):
    if event.key == 'w':
      self.show_w()
    elif event.key == 'r':
      self.show_r()
    elif event.key == 'e':
      self.show_e()
    elif event.key == 'z':
      self.show_z()
    elif event.key == 'x':
      self.show_x()


  def show_w(self):
    ind_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)
    profit_rsp = self._db.get_profit_sheet(self._market, self._code, \
       self._start_date, self._end_date).values()

    fig = plt.figure(1, figsize=(8, 6))
    fig.canvas.set_window_title("{} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    index = 1

    plt.subplot(3, 3, index)
    self._import_data_polyline(ind_rsp, "inv_turn", "存货周转率")
    plt.legend()

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(profit_rsp, "revenue", "营业收入")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(profit_rsp, "oper_cost", "营业成本")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(profit_rsp, "operate_profit", "营业利润")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(profit_rsp, "n_income", "净利润")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(profit_rsp, "n_income", "净利润")
    plt.legend()
    plt.ylim([min_v, max_v])

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()
    
  def show_e(self):
    print("show e")
    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date).values()

    fig = plt.figure(2, figsize=(8, 6))
    fig.canvas.set_window_title("{} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    index = 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "notes_receiv", "应收票据")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "accounts_receiv", "应收账款")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "prepayment", "预付款项")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "oth_receiv", "其他应收款")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "notes_payable", "应付票据")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "acct_payable", "应付账款")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "adv_receipts", "预收款项")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "oth_payable", "其他应付款")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    self._import_data_polyline(balance_rsp, "ind_position", "行业地位")
    plt.legend()

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_z(self):
    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date).values()
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)

    fig = plt.figure(0, figsize=(8, 6))
    fig.canvas.set_window_title("{} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    index = 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "total_hldr_eqy_exc_min_int", "归母所有者权益合计")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "total_hldr_eqy_inc_min_int", "所有者权益合计")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "total_liab_hldr_eqy", "总资产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "fix_assets", "固定资产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "cip", "在建工程")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "const_materials", "工程物资")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "intan_assets", "无形资产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    self._import_data_polyline(indi_rsp, "pro_asset_rate", "生产资产占比")
    plt.legend()

    index += 1
    plt.subplot(3, 3, index)
    self._import_data_polyline(indi_rsp, "pro_asset_profit", "生产资产产出")
    plt.legend()

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_x(self):
    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date).values()
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)
    cash_rsp = self._db.get_cash_flow_sheet(self._market, self._code, \
       self._start_date, self._end_date).values()

    fig = plt.figure(4, figsize=(8, 6))
    fig.canvas.set_window_title("{} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    index = 1
    plt.subplot(3, 3, index)
    self._import_data_polyline(indi_rsp, "cash_insecurity", "现金不安全性")
    plt.legend()

    index += 1
    plt.subplot(3, 3, index)
    self._import_data_polyline(indi_rsp, "rec_insecurity", "应收账款不安全性(月)")
    plt.legend()

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "trad_asset", "交易性金融资产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "fa_avail_for_sale", "可供出售金融资产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "htm_invest", "持有至到期投资")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "invest_real_estate", "投资性房地产")
    plt.legend()
    plt.ylim([min_v, max_v])

    index += 1
    plt.subplot(3, 3, index)
    min_v, max_v = self._import_data_bar(balance_rsp, "lt_eqt_invest", "长期股权投资")
    plt.legend()
    plt.ylim([min_v, max_v])

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

    
  def show_r(self):
    rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)


    fig = plt.figure(3, figsize=(8, 6))
    fig.canvas.set_window_title("{} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

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
    plt.ylim([0, 10])

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()



if __name__ == "__main__":
  s = stock_indicator("SZ", "002029", "", "2010", "2020")
  s.show_z()