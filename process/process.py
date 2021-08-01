import enum
from typing import List

class Priority:
	def __init__(self, level:int, multiintr: bool) -> None:
		self.level = level
		self.enable_multi_intr = multiintr


class ProcessTime:
	"""
	マイクロ秒基準とする
	"""

	def __init__(self, cycle: int, max_proc: int, ave_proc: int = []) -> None:
		self.cycle = cycle
		self.proc_list: List[int] = [max_proc] + ave_proc
		self.proc_idx = 0
		self.proc = self.proc_list[self.proc_idx]

	def next_proc(self):
		self.proc_idx += 1
		if self.proc_idx >= len(self.proc_list):
			self.proc_idx = 0
		self.proc = self.proc_list[self.proc_idx]

	@staticmethod
	def usec(time: int) -> int:
		return time

	@staticmethod
	def msec(time: int) -> int:
		return time * 1000

	@staticmethod
	def sec(time: int) -> int:
		return time * 1000 * 1000

class ProcessState(enum.Enum):
	DORMANT = enum.auto()
	WAITING = enum.auto()			# 時間経過待ち
	READY = enum.auto()				# 優先度高いタスクの待ち状態
	RUNNING = enum.auto()			# 実行中

class TraceInfo:

	def __init__(self, cpu_time: int, state: ProcessState) -> None:
		self.cpu_time = cpu_time				# トレースログ生成時点のCPU時間
		self.state = state						# プロセス状態
		self.time = 0							# プロセス状態タイマ
		# 占有率データ
		self.cycle_delayed = False				# 処理つぶれ
		self.cpu_usage = None					# 占有率
		self.ready_time = None					# READY時間
		self.run_time = None					# RUNNING時間

class Process:

	def __init__(self, id: str, pri: Priority, time: ProcessTime) -> None:
		# プロセス情報
		self.id = id
		self.pri = pri
		self.time = time
		# プロセス状態
		self._state = ProcessState.WAITING
		self._cycle_time = 0						# 起動周期タイマ
		self._ready_time = 0						# 総READY時間タイマ
		self._run_time = 0							# 総RUNNING時間タイマ
		self._cycle_delayed: bool = False			# 処理つぶれ
		# トレース情報
		# プロセスは必ずREADYを経由するので、READY遷移時にログ生成する
		self.trace: TraceInfo = None				# アクティブトレース情報
		self._trace_log: List[TraceInfo] = []		# トレースログ
		self._post_trans(0)
		# 占有率データ
		self._max_usage: TraceInfo = None			# 最大占有率への参照
		self._usage_log: List[TraceInfo] = []		# トレースログ

	def go(self, cpu_time: int, elapse: int):
		"""
		時間経過設定
		"""
		# 経過時間更新
		self._cycle_time += elapse
		if self.trace is not None:
			self.trace.time += elapse
		# 起動周期チェック
		self._check_cycle()
		# 状態判定
		if self._state == ProcessState.WAITING:
			self._check_waiting(cpu_time, elapse)
		elif self._state == ProcessState.READY:
			self._check_ready(cpu_time, elapse)
		elif self._state == ProcessState.RUNNING:
			self._check_running(cpu_time, elapse)

	def _check_cycle(self):
		if self._cycle_time >= self.time.cycle:
			# 状態判定
			if self._state == ProcessState.WAITING:
				# WAITINGでは問題なし
				pass
			elif self._state == ProcessState.READY:
				# READY中に次の起動周期が来てしまったため、処理つぶれが発生している
				self._cycle_delayed = True
			elif self._state == ProcessState.RUNNING:
				# RUNNING中に次の起動周期が来てしまったため、処理つぶれが発生している
				self._cycle_delayed = True
			elif self._state == ProcessState.DORMANT:
				# 不使用
				pass

	def _check_waiting(self, cpu_time: int, elapse: int):
		if self._cycle_time >= self.time.cycle:
			# 起動周期を超えていたらタスク起床
			self.wakeup(cpu_time)
			# 経過時間初期化、次の周期起動カウント開始
			self._cycle_time = 0

	def _check_ready(self, cpu_time: int, elapse: int):
		"""
		上位層からディスパッチされるまでずっと待機
		"""
		self._ready_time += elapse

	def _check_running(self, cpu_time: int, elapse: int):
		"""
		処理時間分だけRUNNING
		"""
		self._run_time += elapse
		#
		if self._run_time >= self.time.proc:
			# 処理時間更新
			self.time.next_proc()
			# WAITING遷移
			self.wait(cpu_time)
			# 占有率情報作成
			self._calc_usage(cpu_time)
			# 処理時間リセット
			self._ready_time = 0
			self._run_time = 0

	def _calc_usage(self, cpu_time: int):
		log = TraceInfo(cpu_time, None)
		log.ready_time = self._ready_time
		log.run_time = self._run_time
		log.cpu_usage = (self._run_time + self._ready_time) / self.time.cycle * 100
		log.cycle_delayed = self._cycle_delayed
		# ログ登録
		self._usage_log.append(log)
		#
		if self._max_usage is None:
			self._max_usage = log
		else:
			if log.cpu_usage > self._max_usage.cpu_usage:
				self._max_usage = log

	def dispatch(self, cpu_time: int):
		"""
		プロセスをアクティブにする
		"""
		# 遷移前処理
		self._pre_trans()
		# 遷移処理
		self._state = ProcessState.RUNNING
		# 遷移後処理
		self._post_trans(cpu_time)

	def preempt(self, cpu_time: int):
		"""
		プロセスをディアクティブする
		"""
		# 遷移前処理
		self._pre_trans()
		# 遷移処理
		self._state = ProcessState.READY
		# 遷移後処理
		self._post_trans(cpu_time)

	def wait(self, cpu_time: int):
		"""
		プロセス終了して次の周期起動待ちに遷移
		"""
		# 遷移前処理
		self._pre_trans()
		# 遷移処理
		self._state = ProcessState.WAITING
		# 遷移後処理
		self._post_trans(cpu_time)

	def wakeup(self, cpu_time: int):
		"""
		待機時間経過でREADYに遷移
		"""
		# 遷移前処理
		self._pre_trans()
		# 遷移処理
		self._state = ProcessState.READY
		# 遷移後処理
		self._post_trans(cpu_time)

	def _pre_trans(self):
		"""
		状態遷移前共通処理
		"""
		# トレースログ更新
		self.trace.cycle_delayed = self._cycle_delayed

	def _post_trans(self, cpu_time: int):
		"""
		状態遷移後共通処理
		"""
		# トレース情報生成
		self.trace = TraceInfo(cpu_time, self._state)
		# ログ登録
		self._trace_log.append(self.trace)

	def is_waiting(self):
		return self._state == ProcessState.WAITING

	def is_ready(self):
		return self._state == ProcessState.READY

	def is_running(self):
		return self._state == ProcessState.RUNNING
