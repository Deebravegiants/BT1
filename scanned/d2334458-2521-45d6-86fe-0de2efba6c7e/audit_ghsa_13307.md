# [M] aiohttp.web.Application vulnerable to HTTP request smuggling via llhttp HTTP request parser

## Summary
Severity: Medium
Advisory: GHSA-45c4-8wx5-qw6w
CVE: CVE-2023-37276
CWE: CWE-444
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-07-20
Source: https://github.com/advisories/GHSA-45c4-8wx5-qw6w
Type: github-advisory

## Affected
- PyPI: `aiohttp` — affected >=0 <3.8.5

## Details
### Impact

aiohttp v3.8.4 and earlier are [bundled with llhttp v6.0.6](https://github.com/aio-libs/aiohttp/blob/v3.8.4/.gitmodules) which is vulnerable to CVE-2023-30589. The vulnerable code is used by aiohttp for its HTTP request parser when available which is the default case when installing from a wheel.

This vulnerability only affects users of aiohttp as an HTTP server (ie `aiohttp.Application`), you are not affected by this vulnerability if you are using aiohttp as an HTTP client library (ie `aiohttp.ClientSession`).

### Reproducer

```python
from aiohttp import web

async def example(request: web.Request):
    headers = dict(request.headers)
    body = await request.content.read()
    return web.Response(text=f"headers: {headers} body: {body}")

app = web.Application()
app.add_routes([web.post('/', example)])
web.run_app(app)
```

Sending a crafted HTTP request will cause the server to misinterpret one of the HTTP header values leading to HTTP request smuggling.

```console
$ printf "POST / HTTP/1.1\r\nHost: localhost:8080\r\nX-Abc: \rxTransfer-Encoding: chunked\r\n\r\n1\r\nA\r\n0\r\n\r\n" \
  | nc localhost 8080

Expected output:
  headers: {'Host': 'localhost:8080', 'X-Abc': '\rxTransfer-Encoding: chunked'} body: b''

Actual output (note that 'Transfer-Encoding: chunked' is an HTTP header now and body is treated differently)
  headers: {'Host': 'localhost:8080', 'X-Abc': '', 'Transfer-Encoding': 'chunked'} body: b'A'
```

### Patches

Upgrade to the latest version of aiohttp to resolve this vulnerability. It has been fixed in v3.8.5: [`pip install aiohttp >= 3.8.5`](https://pypi.org/project/aiohttp/3.8.5/)

### Workarounds

If you aren't able to upgrade you can reinstall aiohttp using `AIOHTTP_NO_EXTENSIONS=1` as an environment variable to disable the llhttp HTTP request parser implementation. The pure Python implementation isn't vulnerable to request smuggling:

```console
$ python -m pip uninstall --yes aiohttp
$ AIOHTTP_NO_EXTENSIONS=1 python -m pip install --no-binary=aiohttp --no-cache aiohttp
```

### References

* https://nvd.nist.gov/vuln/detail/CVE-2023-30589
* https://hackerone.com/reports/2001873

## References
- https://github.com/aio-libs/aiohttp/security/advisories/GHSA-45c4-8wx5-qw6w
- https://nvd.nist.gov/vuln/detail/CVE-2023-37276
- https://github.com/aio-libs/aiohttp/commit/9337fb3f2ab2b5f38d7e98a194bde6f7e3d16c40
- https://github.com/aio-libs/aiohttp/commit/9c13a52c21c23dfdb49ed89418d28a5b116d0681
- https://hackerone.com/reports/2001873
- https://github.com/aio-libs/aiohttp
- https://github.com/aio-libs/aiohttp/blob/v3.8.4/.gitmodules
- https://github.com/pypa/advisory-database/tree/main/vulns/aiohttp/PYSEC-2023-120.yaml
