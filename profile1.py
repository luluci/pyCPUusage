import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

from typing import List

from process.process import Process, Priority, ProcessTime, TraceInfo
from process.process_tracer import ProcessTracer
from process.profiler import Profiler_plantuml

def profiler_test(procs: List[Process]):
	profiler = Profiler_plantuml(procs)
	Process.set_log_callback(profiler.logging)
	tracer = ProcessTracer(procs)
	tracer.run()
	profiler.output()
	#profiler.make_log(tracer)
	#
	#profiler.make_plantuml(tracer)



import queue
import time
import concurrent.futures
from typing import Callable
import pathlib


def profiler_test2(procs: List[Process]):
	profiler = Profiler_plantuml(procs)
	tracer = ProcessTracer(procs)
	q_log = queue.Queue(1000)
	tracing = True

	def log_hdler(log: TraceInfo):
		q_log.put(log)

	def log_thread():
		# ファイルオープン
		p = pathlib.Path("./test.plantuml")
		fp = p.open(mode="w", encoding='utf-8')
		# ヘッダ書き出し
		for line in profiler.pu_header:
			fp.write(line + "\n")
		# 解析ログ取得
		while tracing:
			if not q_log.empty():
				log = q_log.get_nowait()
				profiler.logging(log)
				for line in profiler.pu_body:
					fp.write(line + "\n")
				profiler.pu_body = []
			#time.sleep(0.001)
		# フッタ書き出し
		for line in profiler.pu_footer:
			fp.write(line + "\n")

	Process.set_log_callback(log_hdler)
	executer = concurrent.futures.ThreadPoolExecutor(max_workers=1)
	future_comm_hdle = executer.submit(log_thread)
	#
	try:
		tracer.run()
	except:
		print("except!")
	finally:
		tracing = False
	executer.shutdown()




pri = Priority
time = ProcessTime
us = ProcessTime.usec
ms = ProcessTime.msec
TASK = Process.task
INTR = Process.interrupt


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

if False:
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

if False:
	"""
	test3
	"""
	# Process定義
	procs = [
		Process('Task1', pri(101, False), time(us(550), us(100))),
		Process('Task2', pri(100, True), time(us(500), us(100))),
	]
	# 実行
	profiler_test(procs)

if False:
	"""
	test4
	"""
	# Process定義
	procs = [
		Process('Task1', pri(101, True), time(ms(10), us(800))),
		Process('Task2', pri(100, True), time(us(500), us(400))),
	]
	# 実行
	profiler_test(procs)

if False:
	"""
	test5
	"""
	# Process定義
	procs = [
		Process('Task1', pri(101, True), time(us(1000), us(100))),
		Process('Task2', pri(100, False), time(us(500), us(400))),
	]
	# 実行
	profiler_test(procs)

if True:
	"""
	test6
	"""
	# Process定義
	procs = [
		TASK('TASK1', pri(101, True), time(us(550), us(100))),
		INTR('INTR1', pri(100, True), time(us(500), us(400))),
	]
	# 実行
	profiler_test2(procs)
