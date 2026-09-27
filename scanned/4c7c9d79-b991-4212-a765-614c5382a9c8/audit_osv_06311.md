# [M] Improper validation of IPv6 and IPvFuture addresses

## Summary
Severity: Medium
Advisory: BIT-libpython-2024-11168
Aliases: BIT-python-2024-11168, BIT-python-min-2024-11168, CVE-2024-11168, PSF-2024-13
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-11168
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.11.0 <3.11.4

## Details
The urllib.parse.urlsplit() and urlparse() functions improperly validated bracketed hosts (`[]`), allowing hosts that weren't IPv6 or IPvFuture. This behavior was not conformant to RFC 3986 and potentially enabled SSRF if a URL is processed by more than one URL parser.

## References
- https://github.com/python/cpython/commit/29f348e232e82938ba2165843c448c2b291504c5
- https://github.com/python/cpython/commit/634ded45545ce8cbd6fd5d49785613dd7fa9b89e
- https://github.com/python/cpython/commit/b2171a2fd41416cf68afd67460578631d755a550
- https://github.com/python/cpython/commit/ddca2953191c67a12b1f19d6bca41016c6ae7132
- https://github.com/python/cpython/issues/103848
- https://github.com/python/cpython/pull/103849
- https://mail.python.org/archives/list/security-announce@python.org/thread/XPWB6XVZ5G5KGEI63M4AWLIEUF5BPH4T/
- https://nvd.nist.gov/vuln/detail/CVE-2024-11168
- https://security.netapp.com/advisory/ntap-20250411-0004/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
