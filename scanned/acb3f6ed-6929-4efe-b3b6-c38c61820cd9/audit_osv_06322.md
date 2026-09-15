# [M] URL parser allowed square brackets in domain names

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-0938
Aliases: BIT-python-2025-0938, BIT-python-min-2025-0938, CVE-2025-0938, PSF-2025-1
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-0938
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.2

## Details
The Python standard library functions `urllib.parse.urlsplit` and `urlparse` accepted domain names that included square brackets which isn't valid according to RFC 3986. Square brackets are only meant to be used as delimiters for specifying IPv6 and IPvFuture hosts in URLs. This could result in differential parsing across the Python URL parser and other specification-compliant URL parsers.

## References
- https://github.com/python/cpython/commit/526617ed68cde460236c973e5d0a8bad4de896ba
- https://github.com/python/cpython/commit/90e526ae67b172ed7c6c56e7edad36263b0f9403
- https://github.com/python/cpython/commit/a7084f6075c9595ba60119ce8c62f1496f50c568
- https://github.com/python/cpython/commit/b8b4b713c5f8ec0958c7ef8d29d6711889bc94ab
- https://github.com/python/cpython/commit/d89a5f6a6e65511a5f6e0618c4c30a7aa5aba56a
- https://github.com/python/cpython/commit/ff4e5c25666f63544071a6b075ae8b25c98b7a32
- https://github.com/python/cpython/issues/105704
- https://github.com/python/cpython/pull/129418
- https://mail.python.org/archives/list/security-announce@python.org/thread/K4EUG6EKV6JYFIC24BASYOZS4M5XOQIB/
- https://nvd.nist.gov/vuln/detail/CVE-2025-0938
- https://security.netapp.com/advisory/ntap-20250314-0002/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00013.html
