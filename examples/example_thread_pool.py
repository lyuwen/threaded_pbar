import time
import multiprocessing
from functools import partial
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from threaded_pbar import ThreadedProgressBar


if __name__ == "__main__":
    num_processes = 4
    multiprocessing.set_start_method("spawn")
    def func(rank, pbar):
        for i in range(100):
            pbar.update(1)
            time.sleep(1e-2)
    with ThreadedProgressBar(desc="Test", total=1600, pbar_timeout=1e-4) as pbar:
        with ThreadPoolExecutor(max_workers=num_processes) as pool:
            pool.map(partial(func, pbar=pbar), range(16))

