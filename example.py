import sys
import logging
import uuid
import time
import random
import click

from scyllacache.cache import session, Cache


class Value(object):
    """example class representing pickable objects to be stored as cache values"""
    def __init__(self, id):
        self.id = id
        self.uuid = str(uuid.uuid4())

    @staticmethod
    def calculate():
        """mimicks expensive operation"""
        for _ in range(random.randrange(1, 5)):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1)
        print()

    def __str__(self):
        return "<{id}={uuid}>".format(id=self.id, uuid=self.uuid)


@click.option('--keyspace', required=True, help='Keyspace')
@click.option('--nodes', multiple=True, required=True, help='Scylla nodes/contact points (without port)')
@click.command()
def cli(keyspace, nodes):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    key = 'k{i}'.format(i=random.randrange(1, 5))
    logger.info("request for key {key}".format(key=key))

    with session(nodes=nodes, keyspace=keyspace) as sess:
        cache = Cache(session=sess, ttl=10, logger=logger)

        res, found = cache.get(key)
        if found:
            logger.info("found: %s" % res)
        else:
            logger.info("key {key} not found, calculating value".format(key=key))
            v = Value(id=key)
            v.calculate()
            logger.info("writing %s to cache" % v)
            cache.write(key=key, val=v)


if __name__ == '__main__':
    cli()