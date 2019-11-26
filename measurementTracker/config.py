
class Config(object):
    SECRET_KEY = 'XMLZODSHE8N6NFOZDPZA2HULWSIYJU45K6N4Z19M'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://admin:ddf76mmj@database-1.' \
                              'ckdtooo9sijg.eu-west-1.rds.amazonaws.com/measurementtracker'
    DEBUG = False


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///measurements.db'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    ASSETS_DEBUG = True


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    DEBUG = True

    ASSETS_DEBUG = True
