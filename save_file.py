import os

class indicator_store:

  def __init__(self, file_name):
    self._file_name = file_name

    self._fd = open(self._file_name, "a+")

  def __del__(self):
    self._fd.close()

  def save(self, company):
    self._fd.write("{}\n".format(company))