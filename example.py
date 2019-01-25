import sys
import uuid
import time
import random
import click

from scyllacache.cache import session, Cache

from prometheus_client import start_http_server


class Pickable(object):
    """example class representing pickable objects to be stored as cache values"""
    def __init__(self, id):
        self.id = id
        self.uuid = uuid.uuid4()

    def calculate(self):
        """mimicks expensive operation"""
        for c in range(random.randrange(1, 3)):
            _ = str(self.uuid)[c]
            write('.')
            time.sleep(1)

    def __str__(self):
        return "<{id}={uuid}>".format(id=self.id, uuid=self.uuid)


@click.option('--keyspace', required=True, help='Keyspace')
@click.option('--nodes', multiple=True, required=True, help='Scylla nodes/contact points (without port)')
@click.command()
def cli(keyspace, nodes):
    write("opening session... ")
    with session(nodes=nodes, keyspace=keyspace) as sess:
        print("done")

        cache = Cache(session=sess, ttl=5)

        for c in range(200000):
            c += 1

            key = 'k{i}'.format(i=random.randrange(1, 5))
            write("[{c}] request for key {key}, ".format(c=c, key=key))

            res, found = cache.get(key)
            if found:
                print("found: %s" % res)
            else:
                p = Pickable(id=key)
                p.calculate()
                print(" writing new %s to cache" % p)
                cache.put(key=key, picklable=p)

        write("closing session... ")

    print("done")


def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


if __name__ == '__main__':
    start_http_server(8000)
    cli()
