import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

from typing import List

from process.process import Process, Priority, ProcessTime
from process.process_profiler import ProcessProfiler

pri = Priority
time = ProcessTime
us = ProcessTime.usec
ms = ProcessTime.msec



def profiler_test(procs: List[Process]):
	profiler = ProcessProfiler(procs)
	profiler.run()
	print(f'CPU rate: {profiler.cpu_userate} %')


if False:
	"""
	test1
	"""
	# Process定義
	procs = [
		Process('Task1', pri(101, False), time(us(500), us(100))),
		Process('Task2', pri(100, False), time(us(500), us(100))),
		Process('Task3', pri(5, False), time(ms(100), ms(5))),
		Process('Task4', pri(4, False), time(ms(80), ms(5))),
	]
	# 実行
	profiler_test(procs)

if True:
	"""
	test2
	"""
	# Process定義
	procs = [
		Process('Task1', pri(101, False), time(us(500), us(100))),
		Process('Task2', pri(100, False), time(us(500), us(100))),
	]
	# 実行
	profiler_test(procs)
