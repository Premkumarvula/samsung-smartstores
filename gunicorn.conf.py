"""
Gunicorn config for a t3.micro (2 vCPU / 1GB RAM) instance.

Rule of thumb is (2 x CPU) + 1 workers, but on 1GB RAM total (shared with
Nginx, OneAgent, and the OS) that's too many processes. 2 sync workers is
the safe ceiling here: each Flask+SQLAlchemy worker sits around 60-100MB,
so 2 workers leaves comfortable headroom for the rest of the stack.
"""
import multiprocessing
import os

bind = os.environ.get("GUNICORN_BIND", "127.0.0.1:8000")

workers = int(os.environ.get("GUNICORN_WORKERS", 2))
worker_class = "sync"
threads = int(os.environ.get("GUNICORN_THREADS", 2))

timeout = 30
graceful_timeout = 30
keepalive = 5

max_requests = 500          # recycle workers periodically to bound memory growth
max_requests_jitter = 50

accesslog = "-"              # stdout -> journald -> picked up by Dynatrace log monitoring
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# Belt-and-suspenders sanity check so a runaway worker count never happens.
_cpu_count = multiprocessing.cpu_count()
if workers > (_cpu_count * 2 + 1):
    workers = _cpu_count * 2 + 1
