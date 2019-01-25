import codecs
import pickle
from contextlib import contextmanager
from cassandra.cluster import Cluster
from cassandra.query import named_tuple_factory


class Cache(object):
    query_get_tpl = 'SELECT val FROM {table} WHERE key=? LIMIT 1'
    query_insert_tpl = 'INSERT INTO {table} (key, val) VALUES (?, ?) USING TTL ?'

    def __init__(self, session, table='cache', ttl=86400):
        self.session = session
        self.table = table
        try:
            self.ttl = int(ttl)
        except ValueError:
            raise

        self.session.row_factory = named_tuple_factory

        self.query_get = self.session.prepare(self.query_get_tpl.format(table=self.table))
        self.query_get.fetch_size = 1
        self.query_get.is_idempotent = True

        self.query_insert = self.session.prepare(self.query_insert_tpl.format(table=self.table))

    def get(self, key):
        res = self.session.execute(self.query_get, [key])
        for row in res:
            if row.val:
                # return value of first item
                v = self._unpickle(row.val)
                return v, True
            # if row.val unusable
            return None, False
        # if res iterator empty
        return None, False

    def put(self, key, pickable):
        self._write(key, pickable, self.ttl)

    def _write(self, key, pickable, ttl):
        v = self._pickle(pickable)
        self.session.execute(self.query_insert, [key, v, ttl])

    @staticmethod
    def _pickle(pickable):
        return codecs.encode(pickle.dumps(pickable), "base64").decode()

    @staticmethod
    def _unpickle(p):
        return pickle.loads(codecs.decode(p.encode(), "base64"))


@contextmanager
def session(nodes=[], keyspace='cache'):
    cl = Cluster(contact_points=nodes)
    se = cl.connect(keyspace=keyspace)

    try:
        yield se
    finally:
        cl.shutdown()
