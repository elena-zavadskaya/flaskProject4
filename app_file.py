from app.models import User, Role
from app import create_app, db
# from flask_migrate import Migrate
import unittest
from app.admin import admin

flask_app = create_app('default')

admin.init_app(flask_app)


@flask_app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
