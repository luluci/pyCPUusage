from typing import List
import pathlib

from .process_profiler import ProcessProfiler
from .process import Process, TraceInfo, ProcessState




def make_plantuml(profile: ProcessProfiler):
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
				buff = f'highlight {log.cpu_time} to {log.cpu_time + proc.time.cycle} #Gold;line:DimGrey : 割り込みつぶれ'
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
