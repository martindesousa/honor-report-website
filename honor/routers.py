
import dj_database_url
from django.conf import settings

class HerokuDatabaseRouter:
    def db_for_read(self, model, **hints):
        return 'heroku' if settings.DEBUG is False else 'default'

    def db_for_write(self, model, **hints):
        return 'heroku' if settings.DEBUG is False else 'default'

    def allow_relation(self, obj1, obj2, **hints):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == 'default' or db == 'heroku'
