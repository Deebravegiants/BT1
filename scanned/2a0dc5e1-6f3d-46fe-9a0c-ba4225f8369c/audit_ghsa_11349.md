# [H] Tornado is vulnerable to DoS due to too many multipart parts

## Summary
Severity: High
Advisory: GHSA-qjxf-f2mg-c6mc
CVE: CVE-2026-31958
CWE: CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-qjxf-f2mg-c6mc
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.5

## Details
In versions of Tornado prior to 6.5.5, the only limit on the number of parts in `multipart/form-data` is the `max_body_size` setting (default 100MB). Since parsing occurs synchronously on the main thread, this creates the possibility of denial-of-service due to the cost of parsing very large multipart bodies with many parts. 

Tornado 6.5.5 introduces new limits on the size and complexity of multipart bodies, including a default limit of 100 parts per request. These limits are configurable if needed; see `tornado.httputil.ParseMultipartConfig`. It is also now possible to disable `multipart/form-data` parsing entirely if it is not required for the application.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-qjxf-f2mg-c6mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-31958
- https://github.com/tornadoweb/tornado/commit/119a195e290c43ad2d63a2cf012c29d43d6ed839
- https://github.com/pypa/advisory-database/tree/main/vulns/tornado/PYSEC-2026-140.yaml
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.5
- https://lists.debian.org/debian-lts-announce/2026/04/msg00000.html
