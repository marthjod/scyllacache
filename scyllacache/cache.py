import traceback
from contextlib import ContextDecorator
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory
from cassandra import UnresolvableContactPoints


QUERY_GET = 'SELECT val FROM cache WHERE key=? LIMIT 1'
QUERY_INSERT = 'INSERT INTO cache (key, val) VALUES (?, ?) USING TTL ?'


class Cache(ContextDecorator):
    def __init__(self, nodes, keyspace='cache', logger=None):
        self.logger = logger
        self.nodes = nodes
        self.keyspace = keyspace

    def __enter__(self):
        try:
            self.cluster = Cluster(contact_points=self.nodes)
        except UnresolvableContactPoints as ex:
            self.logger.error(traceback.format_exc(ex))
            return None

        try:
            self.session = self.cluster.connect(keyspace=self.keyspace)
        except Exception as ex:
            self.logger.error(traceback.format_exc(ex))
            return None
        else:
            self.session.row_factory = named_tuple_factory
            self.query_get = self.session.prepare(QUERY_GET)
            self.query_insert = self.session.prepare(QUERY_INSERT)
            return self

    def __exit__(self, *exc):
        try:
            self.cluster.shutdown()
        except Exception as ex:
            self.logger.error(traceback.format_exc(ex))

    def get(self, key):
        res = self.session.execute(self.query_get, [key])
        if len(res.current_rows) > 0:
            return res[0].val, True
        return None, False

    def write(self, key, val):
        res = self.session.execute(self.query_insert, [(key, val)])
        self.logger.info(res)

