import time
from tqdm import tqdm
import multiprocessing
from queue import Queue
from functools import partial
from threading import Thread
from multiprocessing import Pool, Process, Manager
from typing_extensions import TypeAlias


QueueType: TypeAlias = "Queue[Union[None, int]]"


class ThreadedProgressBar:


    def __init__(self, desc=None, total=None, disable=False, unit='it',
                 smoothing=0.3, bar_format=None, initial=0,
                 position=None, pbar_timeout=1e-3, **kwargs):
        self.desc = desc
        self.total = total
        self.disable = disable
        self.unit = unit
        self.smoothing = smoothing
        self.bar_format = bar_format
        self.initial = initial
        self.position = position
        self.kwargs = kwargs

        self.pbar = None
        self.pbar_timeout = pbar_timeout


    @staticmethod
    def _run_threaded_progressbar(
        queue: QueueType,
        timeout: float,
        pbar_args: dict,
    ):
        """Run a progress bar in a separate thread.

        Args:
            queue (QueueType): The queue to increment the progress bars.
            timeout (float): How often to update the progress bars in seconds.
            pbar_args (dict): 
        """

        with tqdm(**pbar_args) as pbar:
            while True:
                item = queue.get()
                if item is None:
                    break
                pbar.update(item)
                time.sleep(timeout)


    def __enter__(self):
        pbar_args = dict(
            desc=self.desc,
            total=self.total,
            disable=self.disable,
            unit=self.unit,
            smoothing=self.smoothing,
            bar_format=self.bar_format,
            initial=self.initial,
            position=self.position,
            **self.kwargs,
            )
        self.manager = multiprocessing.Manager()
        self.pbar_queue: QueueType = self.manager.Queue()
        self.thread = Thread(
            target=self._run_threaded_progressbar, args=(self.pbar_queue, self.pbar_timeout, pbar_args), daemon=True
        )
        self.thread.start()
        return self


    def update(self, value: int):
        self.pbar_queue.put(value)


    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


    def close(self):
        self.pbar_queue.put(None)
        self.thread.join()
        self.manager.shutdown()


if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
    num_processes = 4
    multiprocessing.set_start_method("spawn")
    def func(rank, pbar):
        for i in range(100):
            pbar.update(1)
            time.sleep(1e-2)
    with ThreadedProgressBar(desc="Test", total=1600, pbar_timeout=1e-4) as pbar:
        with ThreadPoolExecutor(max_workers=num_processes) as pool:
            pool.map(partial(func, pbar=pbar), range(16))

