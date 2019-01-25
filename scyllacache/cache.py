import codecs
import pickle
from contextlib import contextmanager

from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory

from prometheus_client import Summary


PROMETHEUS_METRICS_PREFIX = 'scyllacache'


class Cache(object):
    query_get_tpl = 'SELECT val FROM {table} WHERE key=? LIMIT 1'
    query_insert_tpl = 'INSERT INTO {table} (key, val) VALUES (?, ?) USING TTL ?'

    def __init__(self, session, table='cache', ttl=86400, metrics_prefix=PROMETHEUS_METRICS_PREFIX):
        try:
            self.ttl = int(ttl)
        except ValueError:
            raise

        self.session = session
        self.table = table
        self.metrics_prefix = metrics_prefix

        self.session.row_factory = named_tuple_factory

        self.query_get = self.session.prepare(self.query_get_tpl.format(table=self.table))
        self.query_get.fetch_size = 1
        self.query_get.is_idempotent = True

        self.query_insert = self.session.prepare(self.query_insert_tpl.format(table=self.table))

        self.cache_latency = Summary(
            '{prefix}_cache_latency_seconds'.format(prefix=self.metrics_prefix),
            'Cache read/write latency (seconds)', ['op'])
        self.cache_get_latency = self.cache_latency.labels('get')
        self.cache_put_latency = self.cache_latency.labels('put')

        self.pickling_latency = Summary(
            '{prefix}_pickle_latency_seconds'.format(prefix=self.metrics_prefix),
            'Pickling latency (seconds)', ['op'])
        self.pickle_latency = self.pickling_latency.labels('pickle')
        self.unpickle_latency = self.pickling_latency.labels('unpickle')

        self.backend_latency = Summary(
            '{prefix}_backend_latency_seconds'.format(prefix=self.metrics_prefix),
            'Backend read/write request latency (seconds)', ['op'])
        self.backend_read_latency = self.backend_latency.labels('read')
        self.backend_write_latency = self.backend_latency.labels('write')


    def get(self, key):
        with self.cache_get_latency.time():
            res = self._fetch(key)
            for row in res:
                if row.val:
                    # return value of first item
                    v = self._unpickle(row.val)
                    return v, True
                # if row.val unusable
                return None, False
            # if res iterator empty
            return None, False

    def put(self, key, picklable):
        with self.cache_put_latency.time():
            self._write(key, picklable, self.ttl)

    def _fetch(self, key):
        with self.backend_read_latency.time():
            return self.session.execute(self.query_get, [key])

    def _write(self, key, picklable, ttl):
        v = self._pickle(picklable)
        with self.backend_write_latency.time():
            self.session.execute(self.query_insert, [key, v, ttl])

    def _pickle(self, picklable):
        with self.pickle_latency.time():
            return codecs.encode(pickle.dumps(picklable), "base64").decode()

    def _unpickle(self, p):
        with self.unpickle_latency.time():
            return pickle.loads(codecs.decode(p.encode(), "base64"))


@contextmanager
def session(nodes=[], keyspace='cache'):
    cl = Cluster(contact_points=nodes)
    se = cl.connect(keyspace=keyspace)

    try:
        yield se
    finally:
        cl.shutdown()
