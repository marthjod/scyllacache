from contextlib import contextmanager
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory


QUERY_GET = 'SELECT val FROM cache WHERE key=? LIMIT 1'
QUERY_INSERT = 'INSERT INTO cache (key, val) VALUES (?, ?) USING TTL ?'


class Cache(object):
    def __init__(self, session, keyspace='cache', ttl=86400, logger=None):
        self.logger = logger
        self.session = session
        self.keyspace = keyspace
        self.ttl = ttl
        self.session.row_factory = named_tuple_factory
        self.query_get = self.session.prepare(QUERY_GET)
        self.query_insert = self.session.prepare(QUERY_INSERT)

    def get(self, key):
        res = self.session.execute(self.query_get, [key])
        if len(res.current_rows) > 0:
            return res[0].val, True
        return None, False

    def write(self, key, val):
        self._write(key, val, self.ttl)

    def _write(self, key, val, ttl):
        self.session.execute(self.query_insert, [key, val, ttl])


@contextmanager
def session(nodes=[], keyspace='cache'):
    cl = Cluster(contact_points=nodes)
    se = cl.connect(keyspace=keyspace)

    try:
        yield se
    finally:
        cl.shutdown()
