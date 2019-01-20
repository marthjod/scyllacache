import sys
import logging
import uuid
import pickle
import time
import random
import codecs

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


def main(logger):
    keyspace = 'cache'
    key = 'k{i}'.format(i=random.randrange(1, 5))
    logger.info("request for key {key}".format(key=key))

    with session(nodes=['localhost'], keyspace=keyspace) as sess:
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


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    main(logger)
