# [H] multipart vulnerable to ReDoS in `parse_options_header()`

## Summary
Severity: High
Advisory: GHSA-p2m9-wcp5-6qw3
CVE: CVE-2026-28356
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-p2m9-wcp5-6qw3
Type: github-advisory

## Affected
- PyPI: `multipart` — affected >=1.3.0 <1.3.1
- PyPI: `multipart` — affected >=0 <1.2.2

## Details
## Summary

The `parse_options_header()` function in `multipart.py` uses a regular expression with an *ambiguous alternation*, which can cause *exponential backtracking (ReDoS)* when parsing maliciously crafted HTTP or multipart segment headers. This can be abused for **denial of service (DoS)** attacks against web applications using this library to parse request headers or `multipart/form-data` streams.

## Impact

Any WSGI or ASGI application using `multipart.parse_form_data()` directly or indirectly (e.g. while parsing `multipart/form-data` streams) is vulnerable. The slow-down is significant enough to block request handling threads for multiple seconds per request.

## Affected versions

All versions up to and including `1.3.0` are affected. The issue is fixed in `1.2.2`, `1.3.1` and `1.4.0-dev`.

## References
- https://github.com/defnull/multipart/security/advisories/GHSA-p2m9-wcp5-6qw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-28356
- https://github.com/defnull/multipart
