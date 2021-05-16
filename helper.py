import math
from enum import Enum

class ReportedPeriod:
  First_quarter = "0331"
  Mid_quarter = "0630"
  Three_quarter = "0930"
  Annals = "1231"

def fix_num(num, failed_ret=0):
    if num == None or math.isnan(num) or math.isinf(num):
      return failed_ret
    return num

def gen_period(start_year, end_year):
  ret = []
  ps = ["0331", "0630", "0930", "1231"]
  for i_year in range(int(start_year), int(end_year) + 1):
    for p in ps:
      ret.append(str(i_year) + p)
  return ret