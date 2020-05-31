import time


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        print('{!r}:  {:2.2f} s'.format(method.__name__, (te - ts)))
        return result
    return timed