# [H] python-multipart: Quadratic-time querystring parsing with semicolon separators causes CPU denial of service

## Summary
Severity: High
Advisory: GHSA-5rvq-cxj2-64vf
CVE: CVE-2026-53539
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-5rvq-cxj2-64vf
Type: github-advisory

## Affected
- PyPI: `python-multipart` — affected >=0 <0.0.30

## Details
### Summary

When parsing `application/x-www-form-urlencoded` bodies, `QuerystringParser` located the field separator with a two step lookup: it first scanned the entire remaining buffer for `&`, and only when no `&` existed anywhere ahead did it fall back to scanning for `;`. For a body that uses `;` as the separator and contains no `&`, every field iteration performed a full failed `&` scan over the entire remaining buffer before locating the nearby `;`. With N semicolon separated fields in a chunk of size B, this yields O(B^2) byte comparisons per chunk.

An attacker can submit a small crafted body of the form `a;a;a;...` and cause the parser to spend seconds of CPU per request. A handful of concurrent requests can exhaust worker processes.

### Details

In `python_multipart/multipart.py`, both the `FIELD_NAME` and `FIELD_DATA` states located the next separator like this:

```python
sep_pos = data.find(b"&", i)
if sep_pos == -1:
    sep_pos = data.find(b";", i)
```

`data.find(b"&", i)` scans from `i` to the end of the buffer and returns `-1` only when there is no `&` anywhere in the remainder. For a `;` separated body with no `&`, this failed full buffer scan repeats once per field, making parsing quadratic in the body length.

For example, a 1 MiB url encoded body consisting of `a;` repeated ~500,000 times, submitted with `Content-Type: application/x-www-form-urlencoded`, causes the parser to perform on the order of 10^11 byte comparisons, consuming several seconds of CPU for a single request. Cost scales quadratically with chunk size.

The parser is reachable through the public `QuerystringParser` class and through the high level `FormParser`, `create_form_parser`, and `parse_form` APIs for url encoded bodies. It is also the parser Starlette and FastAPI use for `application/x-www-form-urlencoded` request bodies via `request.form()`.

### Impact

Uncontrolled CPU consumption (denial of service). Parsing is synchronous, so a single small crafted form body occupies the handling worker for seconds, blocking any other work on that worker until parsing finishes. Sustained concurrent requests keep workers continuously busy, degrading or denying service.

### Mitigation

Upgrade to `python-multipart` `0.0.30` or later, which treats only `&` as a field separator (per the [WHATWG URL standard](https://url.spec.whatwg.org/#urlencoded-parsing)) using a single bounded scan, making parsing linear in the body length.

## References
- https://github.com/Kludex/python-multipart/security/advisories/GHSA-5rvq-cxj2-64vf
- https://github.com/Kludex/python-multipart
