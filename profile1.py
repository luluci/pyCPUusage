import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), './'))

from typing import List

from process.process import Process, Priority, ProcessTime
from process.process_profiler import ProcessProfiler
from process import tracer

pri = Priority
time = ProcessTime
us = ProcessTime.usec
ms = ProcessTime.msec
TASK = Process.task
INTR = Process.interrupt

def profiler_test(procs: List[Process]):
	profiler = ProcessProfiler(procs)
	profiler.run()
	tracer.make_log(profiler)
	#
	tracer.make_plantuml(profiler)


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
		INTR('INTR1', pri(100, True), time(us(500), us(200))),
	]
	# 実行
	profiler_test(procs)
