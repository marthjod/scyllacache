import sys
import logging
import uuid
import pickle
import time
import random

from scyllacache.cache import session, Cache


class Value(object):
    """example class representing pickable objects to be stored as cache values"""
    def __init__(self, id):
        self.id = id
        self.uuid = uuid.uuid4()

    def pickle(self):
        return str(pickle.dumps(self))

    @staticmethod
    def calculate():
        """mimicks expensive operation"""
        time.sleep(random.randrange(1, 5))


def main(logger):
    keyspace = 'cache'
    keys = ['k-{i}'.format(i=i) for i in range(0, 2)]

    with session(nodes=['localhost'], keyspace=keyspace) as sess:
        cache = Cache(session=sess, ttl=10, logger=logger)

        for key in keys:
            res, found = cache.get(key)
            if found:
                logger.info("found {key}={res}".format(key=key, res=res))
            else:
                logger.info("key {key} not found, calculating value".format(key=key))
                v = Value(id=key)
                v.calculate()
                p = v.pickle()
                logger.info("writing {key}={val} to cache".format(key=key, val=p))
                cache.write(key=key, val=p)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    main(logger)
