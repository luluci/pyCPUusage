import math
import operator

from typing import List

from .process import Process


class ProcessProfiler:
	
	def __init__(self, procs: List[Process]) -> None:
		# Processリスト
		self._procs = sorted(procs, key=operator.attrgetter('pri.level'), reverse=True)
		# 
		self._active_proc: Process = None
		# CPU占有率
		self.cpu_userate: int = 0
		self._cpu_userate_idle: int = 0
		self._cpu_userate_busy: int = 0
		self.proc_start: int = 0

	def run(self):
		# 計測時間決定
		# とりあえずProcess起動周期の最大公倍数とする
		timemax = math.lcm(*[proc.time.cycle for proc in self._procs])
		timemax *= 10
		# us基準で計測時間分ループ
		# 経過時間0から開始
		for cpu_time in range(0,timemax):
			# 起動中プロセスチェック
			self._check_running_proc()
			# ディスパッチチェック
			self._check_dispatch(cpu_time)
			# 最後に時間を進める
			self._go_time(cpu_time)
			# CPU占有率測定
			self._check_cpu_userate(cpu_time)
		# 処理終了後
		self.cpu_userate = self._cpu_userate_busy / (timemax - self.proc_start) * 100

	def _check_running_proc(self):
		"""
		アクティブプロセスの終了チェック
		"""
		if self._active_proc is not None:
			if self._active_proc.is_waiting():
				self._active_proc = None

	def _check_dispatch(self, cpu_time: int) -> int:
		"""
		プロセスディスパッチチェック
		"""
		# 次に起動するプロセスを取得
		proc = self._get_prior_proc()
		# アクティブプロセスと異なればディスパッチを実施
		if proc is not self._active_proc:
			# 現アクティブプロセスをREADYに
			if self._active_proc is not None:
				self._active_proc.preempt(cpu_time)
			# 新アクティブプロセスをRUNNINGに
			if proc is not None:
				proc.dispatch(cpu_time)
			# アクティブプロセス設定
			self._active_proc = proc
			#
			if self.proc_start == 0:
				self.proc_start = cpu_time

	def _get_prior_proc(self) -> Process:
		"""
		RUNNING or READY 状態のプロセスから一番優先度の高いものを選択
		"""
		# 優先度の高い順にソートされている前提で、最初に条件にマッチしたものを選択
		prior = None
		for proc in self._procs:
			if proc.is_running():
				if prior is None:
					# 優先度でソートしている、かつ、最初に検出した有効プロセスになるため、
					# RUNNING中のプロセスが一番優先度が高い
					# このときFCFSは働かないのでRUNNINGを継続
					return proc

			if proc.is_ready() or proc.is_running():
				if prior is None:
					# RUNNINGは直前でチェックしているため、
					# ここでは必ずREADYが最初に見つかった状況になる
					prior = proc
				else:
					if prior.pri.level > proc.pri.level:
						# 優先度でソートされているため、優先度の低いプロセスが出現したら処理終了
						return prior
					elif prior.pri.level < proc.pri.level:
						# 優先度でソートされているため、優先度の高いプロセスは登場しない
						raise Exception("logic error!")
					else:
						# 優先度が同じときFCFS方式でチェック
						if prior.trace.time < proc.trace.time:
							prior = proc
		# RUNNING or READY が見つからなかったらNone
		return prior

	def _go_time(self, cpu_time: int):
		for proc in self._procs:
			# 時間を進める
			proc.go(cpu_time, 1)

	def _check_cpu_userate(self, cpu_time: int):
		"""
		アクティブなプロセスが存在すればbusyが+1
		そうでなければidleが+1
		"""
		if self._active_proc is not None:
			self._cpu_userate_busy += 1
		else:
			self._cpu_userate_idle += 1
