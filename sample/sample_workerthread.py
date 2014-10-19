# The MIT License (MIT)
# Copyright (c) 2014 Nobuyuki Mizoguchi

# -*- coding: utf-8 -*-
from __future__ import print_function
import sys
sys.path.append('../')
from workerthread import WorkersExclusiveQueue, WorkersSharedQueue
import threading
from threading import Thread, Lock
import signal
from functools import partial
import string
import time
import random

num_worker_threads = 10
lk = Lock()
shutdown_event = threading.Event()

class MyResource:
    def __init__(self, i):
        self.worker_id = i

def generate_data():
    length = (int)(random.normalvariate(30, 5))
    data = ''
    for i in range(length):
        data += random.choice(string.letters)
    return data

def display(data):
    lk.acquire()
    print(data)
    lk.release()

def do_job(data, param):
    display('worker %d: %s' % (param.worker_id, data))

def prepare(param):
    display('worker %d is ready for doing job' % param.worker_id)

def handler(workers, signum, frame):
    display('Signal %d received. Will shutdown' % signum)
    workers.join()
    sys.exit(0)

if __name__ == '__main__':
    mode = 0
    if mode == 0:
        workers = WorkersExclusiveQueue(num_worker_threads)
        for i in range(len(workers)):
            workers.set_jobparam(MyResource(i), i)
        for i in range(len(workers)):
            workers.post(prepare, i)
        signal.signal(signal.SIGINT, partial(handler, workers))
        while True:
            for i in range(2 * num_worker_threads):
                workers.post(partial(do_job, generate_data()), i % num_worker_threads)
            workers.join()
            time.sleep(0.5)
            display('If you want to stop posting jobs, input Ctrl-C')
            time.sleep(1)
        workers.join()
    else:
        workers = WorkersSharedQueue(num_worker_threads)
        for i in range(len(workers)):
            workers.set_jobparam(MyResource(i), i)
        for i in range(len(workers)):
            workers.post(prepare)
        signal.signal(signal.SIGINT, partial(handler, workers))
        while True:
            for i in range(2 * num_worker_threads):
                workers.post(partial(do_job, generate_data()))
            workers.join()
            time.sleep(0.5)
            display('If you want to stop posting jobs, input Ctrl-C')
            time.sleep(1)
        workers.join()


