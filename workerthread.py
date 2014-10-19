# The MIT License (MIT)
# Copyright (c) 2014 Nobuyuki Mizoguchi

# -*- coding: utf-8 -*-
from Queue import Queue
from threading import Thread

class Worker:
    def __init__(self, queue):
        self.queue = queue
        self.param = None
    def set_jobparam(self, jobparam):
        self.param = jobparam
    def __call__(self):
        while True:
            job = self.queue.get()
            job(self.param)
            self.queue.task_done()

class WorkersSharedQueue:
    def __init__(self, num_threads):
        self.queue = Queue()
        self.workers = []
        for i in range(num_threads):
            self.workers.append(Worker(q))
            t = Thread(target=self.workers[i])
            t.daemon = True
            t.start()
    def join(self):
        self.queue.join()
    def set_jobparam(self, jobparam, i):
        if i >= len(self.workers):
            raise Exception('Worker list index out of bounds')
        self.workers[i].set_jobparam(jobparam)
    def post(self, job):
        self.queue.put(job)
    def __len__(self):
        return len(self.workers)

class WorkersExclusiveQueue:
    def __init__(self, num_threads):
        self.workers = []
        self.queues = []
        for i in range(num_threads):
            self.queues.append(Queue())
            self.workers.append(Worker(self.queues[i]))
            t = Thread(target=self.workers[i])
            t.daemon = True
            t.start()
    def join(self):
        for i in range(len(self.queues)):
            self.queues[i].join()
    def set_jobparam(self, jobparam, i):
        if i >= len(self.workers):
            raise Exception('Worker list index out of bounds')
        self.workers[i].set_jobparam(jobparam)
    def post(self, job, i):
        if i >= len(self.queues):
            raise Exception('Queue list index out of bounds')
        self.queues[i].put(job)
    def __len__(self):
        return len(self.workers)

