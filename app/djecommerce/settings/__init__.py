from .base import *
import pymysql
pymysql.version_info = (1, 4, 0, "final", 0)

pymysql.install_as_MySQLdb()


env_name = os.getenv('ENV_NAME', 'local')

if env_name == 'production':
    from .production import *
elif env_name == 'base':
    from .base import *
else:
    from .development import *
