from typing import List, Dict
import pathlib

from .process_tracer import ProcessTracer
from .process import Process, TraceInfo, ProcessState


def make_log(profile: ProcessTracer):
	print('[all]')
	buff = f'CPU rate: {profile.cpu_userate} %'
	print(buff)
	print('')
	for i, proc in enumerate(profile._procs):
		print(f'[{proc.id}]')
		print(f'MAX CPU-rate  : {proc._max_usage.cpu_usage} %    (at {proc._max_usage.cpu_time} us)')
		if proc._max_usage.cycle_delayed:
			buff = 'あり'
		else:
			buff = 'なし'
		print(f'割り込みつぶれ: {buff}')


class Profiler_plantuml:

	def __init__(self, procs: List[Process]) -> None:
		# Header(?)作成
		self.pu_header: List[str] = []
		self.pu_header.append("@startuml CPUusage")
		self.pu_header.append("scale 5 as 5 pixels")
		self.last_time_tsk: Dict[int, int] = {}
		# ProcessリストからProcessを一覧化, 最終時間初期化
		for i, proc in enumerate(procs):
			buff = f'robust "{proc.id}" as W{id(proc.id)}'
			self.pu_header.append(buff)
			self.last_time_tsk[id(proc.id)] = -1
		
		# logging情報
		self.pu_body: List[str] = []
		self.last_time = -1
		self.pu_footer: List[str] = []
		self.pu_footer.append("")

	def logging(self, log: TraceInfo):
		# 時間補正:同じプロセス内で時間が重複したら+1して見た目上ずらす
		tim = log.cpu_time
		if self.last_time_tsk[id(log.id)] == log.cpu_time:
			tim += 1
		# プロセス毎時間更新
		self.last_time_tsk[id(log.id)] = log.cpu_time

		# 時間更新判定
		if self.last_time != tim:
			self.pu_body.append('')
			self.pu_body.append(f'@{tim}')
			# 時間更新
			self.last_time = tim
		# 状態変化
		self.pu_body.append(f'W{id(log.id)} is {self._get_state(log.state)}')
		# ハイライト設定
		if log.cycle_delayed:
			buff = f'highlight {log.cpu_time} to {log.cpu_time + log.time} #Gold;line:DimGrey : 割り込みつぶれ({log.id})'
			self.pu_footer.append(buff)

	def _get_state(self, state: ProcessState):
		if state == ProcessState.WAITING:
			return 'WAITING'
		elif state == ProcessState.READY:
			return 'READY'
		elif state == ProcessState.RUNNING:
			return 'RUNNING'
		elif state == ProcessState.DORMANT:
			return 'DORMANT'
		else:
			raise Exception('unknown state!')

	def output(self):
		# enduml
		self.pu_footer.append("@enduml")

		# ファイル出力
		p = pathlib.Path("./test.plantuml")
		with p.open(mode="w", encoding='utf-8') as f:
			for line in self.pu_header:
				f.write(line + "\n")
			for line in self.pu_body:
				f.write(line + "\n")
			for line in self.pu_footer:
				f.write(line + "\n")


def make_plantuml(profile: ProcessTracer):
	"""
	■PlantUML備考(https://plantuml.com/ja/faq)
	・画像サイズはデフォルトで4096まで
	サイズを変更するときは -DPLANTUML_LIMIT_SIZE=8192
	"""

	puml_buff: List[str] = []
	puml_highlight_buff: List[str] = []

	procs = profile._procs

	# startuml
	puml_buff.append("@startuml CPUusage")
	puml_buff.append("scale 5 as 5 pixels")
	for i, proc in enumerate(procs):
		buff = f'robust "{proc.id}" as W{i}'
		puml_buff.append(buff)
	puml_buff.append('')

	# インスタンス毎定義
	for i, proc in enumerate(procs):
		# インスタンス指定
		puml_buff.append(f'@W{i}')
		# 
		for log in proc._trace_log:
			buff = None
			# タイミング設定
			if log.state == ProcessState.WAITING:
				buff = f'{log.cpu_time} is WAITING'
			elif log.state == ProcessState.READY:
				buff = f'{log.cpu_time} is READY'
			elif log.state == ProcessState.RUNNING:
				buff = f'{log.cpu_time} is RUNNING'
			puml_buff.append(buff)
			# ハイライト設定
			if log.cycle_delayed:
				buff = f'highlight {log.cpu_time} to {log.cpu_time + proc.time.cycle} #Gold;line:DimGrey : 割り込みつぶれ({proc.id})'
				puml_highlight_buff.append(buff)
		puml_buff.append('')

	# ハイライト
	puml_buff.extend(puml_highlight_buff)
	# enduml
	puml_buff.append("@enduml")

	# ファイル出力
	p = pathlib.Path("./test.plantuml")
	with p.open(mode="w", encoding='utf-8') as f:
		for line in puml_buff:
			f.write(line + "\n")
