import sys
import logging
from scyllacache.cache import Cache


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


def main():
    keys = ['tm{i}'.format(i=i) for i in range(1, 5)]

    with Cache(nodes=['localhost'], logger=logger) as cache:
        for key in keys:
            res, found = cache.get(key)
            if found:
                logger.info("[{key}] {res}".format(key=key, res=res))
            else:
                logger.warning("[{key}] {res}".format(key=key, res=res))


if __name__ == "__main__":
    main()
