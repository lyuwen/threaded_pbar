import time
import multiprocessing
from functools import partial
from multiprocessing import Pool, Process, Manager
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from threaded_pbar import ThreadedProgressBar


def func(rank, queue, niter=10):
    for i in range(niter):
        #  print(rank, i)
        queue.put(1)
        time.sleep(1e-2)


def simple_func(rank):
    print(rank)


def main(num_workers=4):
  niter = 100
  njobs = 16
  pbar = None
  with Pool(num_workers) as pool:
    queue = (manager := multiprocessing.Manager()).Queue()
    with ThreadedProgressBar(desc="Test", total=niter * njobs, pbar_timeout=1e-4, queue=queue) as pbar:
      pool.map(partial(func, queue=queue, niter=niter), range(njobs))
    queue.put(None)
    manager.shutdown()


class Test:
  def __init__(self, num_workers=4):
    self.num_workers = num_workers
    self.niter = 100
    self.njobs = 16


  def func(self, rank, queue):
      for i in range(self.niter):
          #  print(rank, i)
          queue.put(1)
          time.sleep(1e-2)


  def run(self):
    with Pool(8) as pool:
        queue = (manager := multiprocessing.Manager()).Queue()
        pbar = ThreadedProgressBar(desc="Test", total=self.niter * self.njobs, pbar_timeout=1e-4, queue=queue)
        
        with pbar:
          pool.map(partial(self.func, queue=queue), range(self.njobs))
          queue.put(None)
        manager.shutdown()

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn")
    test = Test(num_workers=8)
    test.run()
    main(num_workers=8)

