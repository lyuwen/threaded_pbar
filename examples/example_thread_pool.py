import time
import multiprocessing
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from threaded_pbar import ThreadedProgressBar


if __name__ == "__main__":
    num_processes = 8
    multiprocessing.set_start_method("spawn")
    niter = 100
    njobs = 16
    def func(rank, pbar):
        for i in range(niter):
            pbar.update(1)
            time.sleep(1e-2)
    queue = (manager := multiprocessing.Manager()).Queue()
    with ThreadedProgressBar(desc="Test", total=niter * njobs, pbar_timeout=1e-4, queue=queue) as pbar:
        with ThreadPoolExecutor(max_workers=num_processes) as pool:
            pool.map(partial(func, pbar=pbar), range(njobs))

