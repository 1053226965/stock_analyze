import matplotlib.pyplot as plt
from adjustText import adjust_text
import sheet_prompt
from stock_db import stock_db
import math
import threading
import helper
from helper import ReportedPeriod

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

  def get_bar_xy(self, start_year, end_year, data, indi_name, period=ReportedPeriod.Annals):
    x = []
    y = []
    min_v = 0x7fffffff
    max_v = -0x7fffffff
    for year in range(start_year, end_year + 1):
      ds = "{}{}".format(year, period)
      indi = data.get(ds, None)
      if indi is None:
        x.append(year)
        y.append(0)
        continue
      min_v = min(min_v, round(indi.get(indi_name, 0) or 0, 1))
      max_v = max(max_v, round(indi.get(indi_name, 0) or 0, 1))
      y.append(round(helper.fix_num(indi.get(indi_name, 0)), 1))
      x.append(year)
    ylabel = ""
    if abs(max_v / 100000000) > 1:
      y = [round(helper.fix_num(y[i]) / 100000000, 1) for i in range(len(y))]
      min_v = min_v / 100000000
      max_v = max_v / 100000000
      ylabel = "亿"
    elif abs(max_v / 10000) > 1:
      y = [int(helper.fix_num(y[i]) / 10000 + 0.5) for i in range(len(y))]
      min_v = min_v / 10000
      max_v = max_v / 10000
      ylabel = "万"
    min_v = min(0, min_v)
    max_v = max_v * 1.2
    return x, y, min_v, max_v, ylabel

  def show_text(self, obj, x, y, color):
    texts = [obj.text(a, b, b, color=color, ha='center', va='bottom', \
      fontdict={'size': 8}) for a, b in zip(x, y)]
    #adjust_text(texts,)

  def deal_axis(self, start_date, end_date, axis, data, indi_name, prompt, type, color="royalblue", period=ReportedPeriod.Annals):
    axis.set_ylabel(prompt, color=color)
    start_year = int(start_date[0:4])
    end_year = int(end_date[0:4])
    if type == "plot":
      x = []
      y = []
      for year in range(start_year, end_year + 1):
        ds = "{}{}".format(year, period)
        indi = data.get(ds, None)
        if indi is None:
          x.append(year)
          y.append(0)
          continue
        y.append(round(indi.get(indi_name, 0), 2))
        x.append(year)
      plt.ylim([min(y), max(y)])
      axis.plot(x, y, color=color, ls='dotted')
    elif type == "bar":
      x, y, min_v, max_v, ylabel = self.get_bar_xy(start_year, end_year, data, indi_name)
      axis.set_ylabel("{}({})".format(prompt, ylabel), color=color)
      min_v = min(0, min_v)
      max_v = max_v * 1.2
      axis.set_ylim(min_v, max_v)
      axis.bar(x, y, color=color)
    return x, y

  def double_y(self, w, h, index, start_date, end_date, \
      ldata, lindi_name, lprompt, ltype, \
      rdata=None, rindi_name=None, rprompt=None, rtype=None, **args):
    period = args.get("period", ReportedPeriod.Annals)
    left_axis = plt.subplot(w, h, index)
    x1, y1 = self.deal_axis(start_date, end_date, left_axis, ldata, lindi_name, lprompt, ltype, "royalblue", period)
    if rdata is not None:
      right_axis = left_axis.twinx() 
      x2, y2 = self.deal_axis(start_date, end_date, right_axis, rdata, rindi_name, rprompt, rtype, "orange", period)
      self.show_text(right_axis, x2, y2, "black")
    self.show_text(left_axis, x1, y1, "crimson")
    return index + 1

  def double_bar(self, w, h, index, start_date, end_date, \
      ldata, lindi_name, lprompt, \
      rdata=None, rindi_name=None, rprompt=None, **args):
    period = args.get("period", ReportedPeriod.Annals)
    bar_width = 0.4
    plt.subplot(w, h, index)
    start_year = int(start_date[0:4])
    end_year = int(end_date[0:4])
    x1, y1, min_v, max_v, ylabel = self.get_bar_xy(start_year, end_year, ldata, lindi_name, period)
    for i in range(len(x1)):
      x1[i] -= bar_width / 2
    plt.bar(x1, y1, bar_width, fc = 'royalblue', label="{}({})".format(lprompt, ylabel))
    if rdata is not None:
      x2, y2, min_v_t, max_v_t, ylabel = self.get_bar_xy(start_year, end_year, rdata, rindi_name)
      for i in range(len(x2)):
        x2[i] += bar_width / 2
      self.show_text(plt, x2, y2, "black")
      plt.bar(x2, y2, bar_width, fc = 'orange', label="{}({})".format(rprompt, ylabel))
      min_v = min(min_v, min_v_t)
      max_v = max(max_v, max_v_t)
    self.show_text(plt, x1, y1, "crimson")
    plt.ylim([min_v, max_v])
    plt.legend()
    return index + 1

  def key_press(self, event):
    if event.key == 'z':
      self.show()
    elif event.key == 'x':
      self.show_x()
    elif event.key == 'c':
      self.show_c()
    elif event.key == 'v':
      self.show_v()
    elif event.key == 'b':
      self.show_b()
    elif event.key == 'n':
      self.show_n()

  def show(self):
    fig = plt.figure(0, figsize=(8, 6))
    fig.canvas.set_window_title("负债相关 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)

    index = 1
    index = self.double_y(3, 3, index, self._start_date[0:4], self._end_date, \
      indi_rsp, "cash_insecurity", "短期负债/现金", "plot")
    index = self.double_y(3, 3, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "st_borr", "短期借款", "bar")
    index = self.double_y(3, 3, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "lt_borr", "长期借款", "bar")
    index = self.double_y(3, 3, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "non_cur_liab_due_1y", "一年内到期的非流动负债", "bar")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_x(self):
    fig = plt.figure(1, figsize=(8, 6))
    fig.canvas.set_window_title("盈利相关 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    profit_rsp = self._db.get_profit_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)

    index = 1
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "revenue", "营业收入", "bar", \
      indi_rsp, "tr_yoy", "同比增长", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "operate_profit", "营业利润", "bar", \
      indi_rsp, "op_of_gr", "同比增长", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "n_income_attr_p", "净利润", "bar", \
      indi_rsp, "netprofit_yoy", "同比增长", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      indi_rsp, "grossprofit_margin", "毛利率", "plot", \
      indi_rsp, "netprofit_margin", "净利率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      indi_rsp, "roe", "roe", "plot", \
      indi_rsp, "roa", "roa", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "total_hldr_eqy_exc_min_int", "净资产", "bar", \
      indi_rsp, "equity_yoy", "同比增长", "plot")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_c(self):
    fig = plt.figure(2, figsize=(8, 6))
    fig.canvas.set_window_title("管理相关 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)

    index = 1
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "accounts_receiv", "应收账款", "bar", \
      indi_rsp, "ar_turn", "应收账款周转率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "inventories", "存货", "bar", \
      indi_rsp, "inv_turn", "存货周转率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "fix_assets", "固定资产", "bar", \
      indi_rsp, "fa_turn", "固定资产周转率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "total_assets", "总资产", "bar", \
      indi_rsp, "assets_turn", "总资产周转率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      balance_rsp, "total_liab", "负债", "bar", \
      indi_rsp, "debt_to_assets", "资产负债率", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      indi_rsp, "assets_to_eqt", "权益乘数", "bar")
    
    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_v(self):
    fig = plt.figure(3, figsize=(8, 6))
    fig.canvas.set_window_title("现金流 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    balance_rsp = self._db.get_balance_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)
    profit_rsp = self._db.get_profit_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    cash_rsp = self._db.get_cash_flow_sheet(self._market, self._code, \
       self._start_date, self._end_date)

    total_income = 0
    total_income_cash = 0
    for p in profit_rsp.values():
      total_income += helper.fix_num(p["n_income_attr_p"])
    for p in cash_rsp.values():
      total_income_cash += helper.fix_num(p["n_cashflow_act"])
    index = 1
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "n_income_attr_p", "净利润", \
      cash_rsp, "n_cashflow_act", "经营现金流")
    plt.title("净和:{} 现金和:{} 差值:{}".format(total_income, \
      total_income_cash, total_income - total_income_cash))
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "revenue", "营业收入", \
      cash_rsp, "c_fr_sale_sg", "销售商品、提供劳务收到的现金")
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      cash_rsp, "c_cash_equ_end_period", "现金及现金等价物余额", \
      balance_rsp, "interest_liab", "有息负债")
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      cash_rsp, "n_incr_cash_cash_equ", "现金及现金等价物净增加额")
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      cash_rsp, "n_cashflow_inv_act", "投资现金流")
    index = self.double_bar(3, 2, index, self._start_date[0:4], self._end_date, \
      cash_rsp, "n_cash_flows_fnc_act", "筹集现金流")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_b(self):
    fig = plt.figure(4, figsize=(8, 6))
    fig.canvas.set_window_title("费用相关 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)

    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)
    profit_rsp = self._db.get_profit_sheet(self._market, self._code, \
       self._start_date, self._end_date)
    
    index = 1
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "sell_exp", "销售费用", "bar", \
      indi_rsp, "saleexp_to_gr", "销售费用/营业总收入", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "admin_exp", "管理费用", "bar", \
      indi_rsp, "adminexp_of_gr", "管理费用/营业总收入", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "fin_exp", "财务费用", "bar", \
      indi_rsp, "finaexp_of_gr", "财务费用/营业总收入", "plot")
    index = self.double_y(3, 2, index, self._start_date[0:4], self._end_date, \
      profit_rsp, "all_exp", "三费用", "bar", \
      indi_rsp, "all_exp_gr", "三费用/营业总收入", "plot")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

  def show_n(self):
    fig = plt.figure(5, figsize=(8, 6))
    fig.canvas.set_window_title("毛利率 {} {} {}".format(self._market, self._code, self._name))
    fig.canvas.mpl_connect('key_press_event', self.key_press)
    
    index = 1

    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date, ReportedPeriod.First_quarter)
    index = self.double_bar(2, 2, index, self._start_date, self._end_date, \
      indi_rsp, "grossprofit_margin", "第一季度毛利率", \
        indi_rsp, "netprofit_margini", "第一季度净利率", period=ReportedPeriod.First_quarter)
    
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date, ReportedPeriod.Mid_quarter)
    index = self.double_bar(2, 2, index, self._start_date, self._end_date, \
      indi_rsp, "grossprofit_margin", "中季度毛利率", \
        indi_rsp, "netprofit_margin", "中季度净利率", period=ReportedPeriod.Mid_quarter)
    
    indi_rsp = self._db.get_annals_indicator(self._market, self._code, \
       self._start_date, self._end_date)
    index = self.double_bar(2, 2, index, self._start_date, self._end_date, \
      indi_rsp, "grossprofit_margin", "年度毛利率", \
        indi_rsp, "netprofit_margin", "年度净利率")

    figManager = plt.get_current_fig_manager()
    figManager.window.showMaximized()
    plt.show()

if __name__ == "__main__":
  s = stock_indicator("SH", "603208", "", "2010", "2020")
  #s = stock_indicator("SH", "601155", "", "2010", "2020")
  s.show_b()