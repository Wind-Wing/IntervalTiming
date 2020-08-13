import queue
import threading
import os

num_worker_threads = 2


def train_model(rule_group, w2_reg, r2_reg, index):
    run_cmd = 'python3 core_multitasking/cluster_training_unit.py '+rule_group+' '+str(w2_reg)+' '+str(r2_reg)+' '+str(index)
    os.system(run_cmd)


#####################################################################
parameter_list = list()

def set_parameter_list(rule_group_name, indexes=list(range(0, 16)), w2_reg_list=[0], r2_reg_list=[0]):
    for w2_reg in w2_reg_list:
        for r2_reg in r2_reg_list:
            for index in indexes:
                parameter_list.append((rule_group_name, w2_reg, r2_reg, index))

set_parameter_list('space', indexes=[0])
set_parameter_list('decision_making', indexes=[0])

#####################################################################


def worker():
    while True:
        item = q.get()
        if item is None:
            break
        train_model(*item)
        q.task_done()


q = queue.Queue()

threads = []
for i in range(num_worker_threads):
    t = threading.Thread(target=worker)
    t.start()
    threads.append(t)


for item in parameter_list:
    q.put(item)


# block until all tasks are done
q.join()

# stop workers
for i in range(num_worker_threads):
    q.put(None)
for t in threads:
    t.join()
