# [M] Django REST framework: Potential bypass of Django `DATA_UPLOAD_MAX_MEMORY_SIZE` when parsing oversized JSON and urlencoded request bodies via DRF `request.data`

## Summary
Severity: Medium
Advisory: GHSA-2m8g-3cmr-wg3w
CVE: CVE-2026-73228
CWE: CWE-400, CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-2m8g-3cmr-wg3w
Type: github-advisory

## Affected
- PyPI: `djangorestframework` — affected >=0 <3.17.2

## Details
## Summary

While investigating Django REST Framework's request parsing behavior, I identified that DRF's high-level `request.data` parsing appears to bypass Django's configured `DATA_UPLOAD_MAX_MEMORY_SIZE` protection for `application/json` and `application/x-www-form-urlencoded` request bodies.

In the tested configurations, Django correctly raises `RequestDataTooBig` when applications access `request.body` or Django's native `request.POST`, but DRF successfully parses the same oversized payloads through `request.data`.

This behavior appears to occur because DRF passes the underlying `HttpRequest` object directly to parsers, which consume the request stream through Django's lower-level streaming interface rather than the guarded `request.body` path.

I am reporting this privately because I am unsure whether this behavior is considered part of DRF's intended security boundary, but it appears to bypass a documented Django request-size protection for common DRF request parsing paths and may have availability implications.


# What I Verified

I verified the behavior locally using the following combinations:

* Django **6.0.7** + DRF **3.17.1** → **Affected**
* Django **6.0.7** + DRF **current upstream main** → **Affected**

For both versions, the observed behavior was:

```
Django request.body
→ RequestDataTooBig

Django request.POST (application/x-www-form-urlencoded)
→ RequestDataTooBig

Django request.read()
→ Reads the entire oversized request body

DRF request.data
→ Successfully parses oversized JSON and urlencoded request bodies
```

I also confirmed that:

* `multipart/form-data` remains protected because DRF delegates multipart parsing to Django's multipart parser.
* The behavior reproduces on both direct WSGI and ASGI servers without a reverse proxy or external request-size middleware.


# Technical Details

The relevant execution flow is:

```
APIView

↓

rest_framework.request.Request

↓

request.data

↓

Request._load_data_and_files()

↓

Request._parse()

↓

Request._load_stream()

↓

self._stream = self._request

↓

JSONParser.parse(...)
or
FormParser.parse(...)

↓

stream.read() / json.load(...)
```

The important implementation detail is that DRF assigns the original Django `HttpRequest` object as the parser stream.

Unlike `request.body` and Django's native form parsing, consuming the stream through `HttpRequest.read()` does not trigger Django's `RequestDataTooBig` protection.

As a result, DRF's built-in parsers successfully consume oversized request bodies that Django itself would reject through its higher-level request interfaces.


# Reproduction Steps

## Environment

Python 3.13

Django 6.0.7

Django REST Framework 3.17.1 (also reproduced on current upstream main)

Configure:

```python
DATA_UPLOAD_MAX_MEMORY_SIZE = 10
```

Create a simple DRF API view:

```python
from rest_framework.views import APIView
from rest_framework.response import Response

class DemoView(APIView):
    def post(self, request):
        return Response(request.data)
```

Start the application.

Send an oversized JSON request:

```
POST /demo
Content-Type: application/json
Content-Length: >10 bytes
```

Example:

```json
{
  "value": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA..."
}
```

Observed:

```
HTTP 200

JSON successfully parsed
```

Now compare against:

```python
request.body
```

Observed:

```
RequestDataTooBig
```

Likewise, compare against:

```python
request.POST
```

using

```
application/x-www-form-urlencoded
```

Observed:

```
RequestDataTooBig
```

This demonstrates different enforcement depending on which request API is used.


# Root Cause

Django documents `HttpRequest.read()` as a streaming interface.

DRF exposes `request.data` as the primary high-level request parsing API.

Currently, DRF forwards the raw Django request stream directly to parsers before any request-size validation equivalent to Django's `request.body` path occurs.

Consequently:

* JSONParser
* FormParser

fully consume oversized request bodies despite Django's configured request-size limit.


# Security Impact

This does **not** appear to introduce:

* Authentication bypass
* Authorization bypass
* Remote code execution
* Information disclosure
* Integrity compromise

However, it may reduce the effectiveness of deployments relying on Django's `DATA_UPLOAD_MAX_MEMORY_SIZE` to limit request-body resource consumption.

Potential consequences include:

* Additional memory allocation during JSON parsing
* Additional CPU usage while decoding large JSON payloads
* Increased resource consumption when handling oversized request bodies
* Reduced effectiveness of Django's configured request-size protection for DRF endpoints using `request.data`

The practical impact depends on deployment configuration, including:

* upstream request-size limits
* reverse proxy configuration
* authentication
* rate limiting
* endpoint exposure


# Memory Observations

During local testing I observed successful parsing of oversized request bodies despite the configured limit.

Representative measurements showed significantly increased memory allocation while parsing large JSON and urlencoded payloads.

I intentionally did **not** perform destructive concurrency testing or attempt to exhaust system resources.


# Scope

Confirmed affected:

* application/json
* application/x-www-form-urlencoded

Confirmed not affected:

* multipart/form-data


# Suggested Fix Direction

One possible approach would be for DRF to enforce Django's configured `DATA_UPLOAD_MAX_MEMORY_SIZE` before handing the raw request stream to parsers that fully materialize request bodies in memory.

This would preserve Django's configured request-size protection for the common `request.data` API without requiring broader changes to Django's documented streaming interface.


# Versions Tested

Affected:

* Django 6.0.7 + DRF 3.17.1
* Django 6.0.7 + DRF current upstream main

I did not perform a complete historical version bisect.


# Disclosure

I have not publicly disclosed this behavior.

I am submitting it privately in accordance with the project's security policy because I am unsure whether maintainers consider this part of DRF's intended security boundary.

# Note:

**Thank you for taking the time to review this report.**

If you determine that this behavior should be addressed, I would be happy to help investigate further, develop a fix, add regression tests, and submit a patch if you'd find that helpful.

I have experience as a **Python/Django software engineer, security researcher, and open-source contributor**, and I'd be glad to contribute if you think that would be useful.

## References
- https://github.com/encode/django-rest-framework/security/advisories/GHSA-2m8g-3cmr-wg3w
- https://nvd.nist.gov/vuln/detail/CVE-2026-73228
- https://github.com/encode/django-rest-framework/pull/10013
- https://github.com/encode/django-rest-framework/commit/2912dc98042f78e27636551fc22eeaf10f725fdd
- https://github.com/encode/django-rest-framework/commit/82ef7b7e4e0a73ba5c489b465fae7e76d948da4e
- https://github.com/encode/django-rest-framework
- https://github.com/encode/django-rest-framework/releases/tag/3.17.2
