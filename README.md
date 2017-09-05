## Checklist

- [x] I have verified that that issue exists against the `master` branch of Django REST framework.
- [x] I have searched for similar issues in both open and closed tickets and cannot find a duplicate.
- [x] This is not a usage question. (Those should be directed to the [discussion group](https://groups.google.com/forum/#!forum/django-rest-framework) instead.)
- [x] This cannot be dealt with as a third party library. (We prefer new functionality to be [in the form of third party libraries](http://www.django-rest-framework.org/topics/third-party-resources/#about-third-party-packages) where possible.)
- [x] I have reduced the issue to the simplest possible case.
- [ ] I have included a failing test as a pull request. (If you are unable to do so we can still accept the issue.)

## Versions

Django 1.11.x

DRF: 3.6.4, and ``master`` branch on Github

## Steps to reproduce

1. Clone the project at https://github.com/lddubeau/drf_pickling_error.git

2. Optionally, create a virtual environment and switch to it before
running `pip`.

3. Install Django and DRF:

```
pip install Django
pip install djangorestframework
```

(You could also install DRF from the master branch of the Github
repo. The results are the same.)

4. Change directory to `drf_pickling_error/myproject`.

5. `./manage.py migrate`

6. `./manage.py createcachetable`.

7. `./manage.py runserver localhost:some.port.that.suits.you`

8. Access the root of the site.

## Expected behavior

No errors when accessing the root of the project.

## Actual behavior

Accessing the root of the site results in the following failure:

```
Internal Server Error: /
Traceback (most recent call last):
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/core/handlers/exception.py", line 41, in inner
    response = get_response(request)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/utils/deprecation.py", line 142, in __call__
    response = self.process_response(request, response)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/middleware/cache.py", line 102, in process_response
    lambda r: self.cache.set(cache_key, r, timeout)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/template/response.py", line 94, in add_post_render_callback
    callback(self)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/middleware/cache.py", line 102, in <lambda>
    lambda r: self.cache.set(cache_key, r, timeout)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/core/cache/backends/db.py", line 87, in set
    self._base_set('set', key, value, timeout)
  File "/home/ldd/src/django_issues/pickling_error/venv/local/lib/python2.7/site-packages/django/core/cache/backends/db.py", line 114, in _base_set
    pickled = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
PicklingError: Can't pickle <type 'function'>: attribute lookup __builtin__.function failed
```

## Observations

The case above was produced from a large application that ran fine
until I started making the changes to move from Django 1.10 to Django
1.11.

The problem occurs because when the caching machinery serializes a DRF
`Response` object, it also tries to serialize the `data` field of the
DRF object, which in the case of responses that are to be rendered
with a template can be just about anything under the sun. In the
example code here, a `Form` ends up being serialized, which was fine
in Django 1.10 but not in Django 1.11.

Conceptually, I don't see any reason why the `data` field should be
part of the data passed to Django for caching. By the time caching is
done, response should be rendered and the rendering should be final so
there should be no reason to access `data` from a response retreived
from the cache.

I've set a second path in the `urls.py` file for `/foo` which does
essentially the same thing that the `/` path (which uses DRF) does,
but it does not use any of the DRF machinery. It works just fine.
When I trace what happens during serialization, I see that Django does
not try to serialize the form.
