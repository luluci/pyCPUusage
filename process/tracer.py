from typing import List

import matplotlib.pyplot as plt

from .process_profiler import ProcessProfiler
from .process import Process, TraceInfo


def make_graph(profile: ProcessProfiler):

	row_count = len(profile._procs)

	y_label = ['DORMANT', 'WAITING', 'READY', 'RUNNING']
	y_label = [1,2,3,4]
	x_label = [time for time in range(0,profile.proc_end)]

	fig, axis = plt.subplots(row_count, sharex=True)
	for i, proc in enumerate(profile._procs):
		data = tracelog_to_data(proc._trace_log)

		axis[i].plot(x_label, data, label=proc.id)
		axis[i].set_xticks(x_label)
		#axis[i].set_yticks(data)
		axis[i].set_yticks(y_label)
		axis[i].spines['right'].set_visible(False)              # 右枠非表示
		axis[i].spines['top'].set_visible(False)                # 上枠非表示
		axis[i].spines['bottom'].set_visible(False)             # 下枠非表示
		axis[i].legend()                                        # 凡例表示
		axis[i].grid(linestyle='--')                            # グリッド線表示

	# 縦方向に、間隔を密にグラフをレイアウト
	fig.subplots_adjust(hspace=0.1)

	# グラフ表示
	plt.show()
	plt.savefig("test.png")


def tracelog_to_data(logs: List[TraceInfo]) -> List[int]:
	data = []
	for log in logs:
		data.extend(state_to_num(log))
	return data

def state_to_num(log: TraceInfo) -> List[int]:
	return [log.state.value] * log.time
