import sys
import logging
import uuid

from scyllacache.cache import session, Cache


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    keyspace = 'cache'
    keys = ['k-{i}'.format(i=i) for i in range(0, 2)]

    with session(nodes=['localhost'], keyspace=keyspace) as sess:
        cache = Cache(session=sess, ttl=10, logger=logger)

        for key in keys:
            res, found = cache.get(key)
            if found:
                logger.info("[{key}] {res}".format(key=key, res=res))
            else:
                cache.write(key=key, val=str(uuid.uuid4()))


if __name__ == "__main__":
    main()
