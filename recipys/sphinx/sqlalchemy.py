'''
Using the @declared_attr and @func.expression decorators in a mixin can cause
Sphinx-doc to fail if the attribute in question is attempting to access a class
attribute belonging to a child class before the mixin is inherited.

Example:

    .. code::python

        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy import func, cast, overlay, 

        Base = declarative_base()

        class UTCTimeMixin(object):
            @hybrid_property
            def start_time_utc(self):
                """ Return the start time at UTC as text. """
                if self.start_time is None:
                    return self.start_time

                return (self.start_time
                        .astimezone(tz.tzutc())
                        .isoformat()
                        .replace('+00:00', 'Z'))

            @start_time_utc.expression
            def start_time_utc(cls):
                """ Return the start time at UTC as text. """
                return case(
                    [(cls.start_time == None, None)],
                    else_=overlay(
                        cast(func.timezone('utc', cls.start_time),
                             Unicode) + 'Z',
                        'T', 11, 1))

        class DumbClass(UTCTimeMixin, Base):
            __tablename__ = '__dummy__'
            start_time = Column(DateTime(True))

The UTCTimeMixin is inherited by DumbClass but start_time_utc tries to access
start_time. UTCTimeMixin has no attribute named start_time so sphinx's inspect
module will raise:

> AttributeError: start_time_utc

Upon inspection of sphinx's source code we see this:

  .. code::python

      def safe_getattr(obj, name, *defargs):
          """A getattr() that turns all exceptions into AttributeErrors."""
          try:
              return getattr(obj, name, *defargs)
          except Exception as e:
              # this is a catch-all for all the weird things that some modules do
              # with attribute access
              if defargs:
                  return defargs[0]
              raise AttributeError(name)

Accessing start_time_utc executes it and raises an Attribute Error on
cls.start_time. This in turn is reraised by safe_getattr as an Attribute error
on start_time_utc.

Solution
========

start_time_utc can be replaced at runtime with a mock function that does
nothing and has same doc string. This can be hooked in to autodoc-skip-member
event.

In conf.py add

.. code::python

    from functools import partial
    from recipys.sphinx import ignore_getattr

    IGNORE_ERRORS_FOR = {'UTCTimeMixin': ('start_time_utc',)}
    ignore_getattr = partial(ignore_getattr, IGNORE_ERRORS_FOR)

    def setup(app):
        app.connect('autodoc-skip-member', ignore_getattr)


Pitfalls
========

Sphinx will not include any decorators or paramaters as a part of the
documentation for any attributes that have to be replaced with a mock function
but some documentation is better than no documentation.
'''


def ignore_getattr(ignore_errors_for, app, what, name, obj, skip, options):
    for attribute_name in ignore_errors_for.get(name, []):
        try:
            getattr(obj, attribute_name)
        except AttributeError:
            # Only patch ``obj`` if ``getattr`` fails.
            def mock_function():
                """ Docstring inserted here. """
            mock_function.__doc__ = obj.__dict__.get(attribute_name).__doc__
            setattr(obj, attribute_name, mock_function)
