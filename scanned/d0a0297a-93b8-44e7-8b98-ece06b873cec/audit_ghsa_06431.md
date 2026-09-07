# [H]  Tornado: Urlencoded body parsing omits max_num_fields, so one request can stall the event loop

## Summary
Severity: High
Advisory: GHSA-mpf4-983q-p7j4
CVE: CVE-2026-82397
CWE: CWE-1284, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-mpf4-983q-p7j4
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.8

## Details
## Summary

Tornado parses `application/x-www-form-urlencoded` bodies with `urllib.parse.parse_qs` and does not pass `max_num_fields`. A body made almost entirely of separators produces tens of millions of fields, and the parse happens on the event loop before the handler runs, so a single request stalls the whole server.

## Where it is

`tornado/escape.py`, at HEAD `e530031405e2154654dedc4c84d5656b557ea310`:

```python
result = urllib.parse.parse_qs(
    qs, keep_blank_values, strict_parsing, encoding="latin1", errors="strict"
)
```

`max_num_fields` is the parameter CPython added for exactly this, and it is absent.

The path to it is entirely server-side and pre-dispatch. `RequestHandler._execute` parses the body at `tornado/web.py:1821`, which reaches `HTTPServerRequest._parse_body` at `tornado/httputil.py:636`, and the urlencoded branch of `parse_body_arguments` calls `parse_qs_bytes` at `tornado/httputil.py:1030`.

The size that reaches it is bounded only by the body cap, which defaults to the stream's `max_buffer_size` of 104857600 at `tornado/iostream.py:239`, applied as the request body default at `tornado/http1connection.py:136-140`. A 100 MB body of separators is around fifty million fields.

## Impact

Denial of service against the whole process, not one request. Tornado is single-threaded and the parse is synchronous on the event loop, so every other connection waits. No authentication is needed if any route accepts a form post, which is the normal case.

## Suggested fix

Pass a bound:

```python
result = urllib.parse.parse_qs(
    qs, keep_blank_values, strict_parsing, encoding="latin1", errors="strict",
    max_num_fields=max_num_fields,
)
```

with a conservative default and a way for applications to raise it. CPython raises `ValueError` when the limit is exceeded, which maps cleanly onto a 400.

Lowering the default body cap for urlencoded specifically would help too, since 100 MB of form fields is not a shape any real client sends.

## Why I do not think this is a duplicate

The published tornado advisories cover out-of-bounds access in the C extension, unbounded accumulation of decompressed chunks in `AsyncHTTPClient`, the Authorization header surviving cross-origin redirects, credential leakage on curl handle reuse, and cookie attribute validation. The decompression one is the nearest in spirit and is on the client side; this is the server parsing a request body. The call is unchanged at HEAD.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-mpf4-983q-p7j4
- https://nvd.nist.gov/vuln/detail/CVE-2026-82397
- https://github.com/tornadoweb/tornado/pull/3704
- https://github.com/tornadoweb/tornado/commit/8d6363ed7b69d5f0da806efe34d256627a2191de
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.8
