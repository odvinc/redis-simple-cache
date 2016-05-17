import redis


class CacheMissException(Exception):
    pass


class RedisNoConnException(Exception):
    pass


class RedisConnect(object):

    def __init__(self, host=None, port=None, db=None, password=None):
        self.host = host if host else 'localhost'
        self.port = port if port else 6379
        self.db = db if db else 0
        self.password = password

    def connect(self):

        try:
            redis.StrictRedis(host=self.host, port=self.port, password=self.password).ping()
        except redis.ConnectionError:
            raise RedisNoConnException("Failed to create connection to redis",
                                       (self.host,
                                        self.port)
            )
        return redis.StrictRedis(host=self.host,
                                 port=self.port,
                                 db=self.db,
                                 password=self.password)


class SimpleCache(object):

    def __init__(self, expire=None, host=None, port=None, db=None, password=None,
                 namespace='redis-cache'):

        self.expire = expire
        self.prefix = namespace
        self.host = host
        self.port = port
        self.db = db

        try:
            self.connection = RedisConnect(host=self.host,
                                           port=self.port,
                                           db=self.db,
                                           password=password).connect()
        except RedisNoConnException:
            self.connection = None
            pass

    def make_key(self, key):
        return "{0}:{1}".format(self.prefix, key)

    def get(self, key):

        value = self.connection.get(self.make_key(key))
        if value is None:
            raise CacheMissException
        else:
            return value

    def store(self, key, value, expire=None):

        if expire is None:
            expire = self.expire

        if (isinstance(expire, int) and expire <= 0) or (expire is None):
            self.connection.set(self.make_key(key), value)
        else:
            self.connection.setex(self.make_key(key), expire, value)