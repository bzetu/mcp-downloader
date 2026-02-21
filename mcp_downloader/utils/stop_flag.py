import threading

_stop_flag = threading.Event()


def set_stop():
    _stop_flag.set()


def is_stopped():
    return _stop_flag.is_set()


def reset():
    _stop_flag.clear()
