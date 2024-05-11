from app.models import User, Role
from app import create_app, db
import unittest
flask_app = create_app('default')


@flask_app.cli.command('test')
def test():
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)