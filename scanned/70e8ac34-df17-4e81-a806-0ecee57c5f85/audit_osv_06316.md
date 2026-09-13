# [M] Buffer overread when using an empty list with SSLContext.set_npn_protocols()

## Summary
Severity: Medium
Advisory: BIT-libpython-2024-5642
Aliases: BIT-python-2024-5642, BIT-python-min-2024-5642, CVE-2024-5642, PSF-2024-6
Ecosystem: Bitnami
Published: 2025-10-14
Source: https://osv.dev/vulnerability/BIT-libpython-2024-5642
Type: osv

## Affected
- Bitnami: `libpython` — affected >=0 <3.9.24

## Details
CPython 3.9 and earlier doesn't disallow configuring an empty list ("[]") for SSLContext.set_npn_protocols() which is an invalid value for the underlying OpenSSL API. This results in a buffer over-read when NPN is used (see CVE-2024-5535 for OpenSSL). This vulnerability is of low severity due to NPN being not widely used and specifying an empty list likely being uncommon in-practice (typically a protocol name would be configured).

## References
- http://www.openwall.com/lists/oss-security/2024/06/28/4
- https://github.com/python/cpython/commit/39258d3595300bc7b952854c915f63ae2d4b9c3e
- https://github.com/python/cpython/commit/a2cdbb6e8188ba9ba8b356b28d91bff60e86fe31
- https://github.com/python/cpython/issues/121227
- https://github.com/python/cpython/pull/23014
- https://jbp.io/2024/06/27/cve-2024-5535-openssl-memory-safety.html
- https://mail.python.org/archives/list/security-announce@python.org/thread/PLP2JI3PJY33YG6P5BZYSSNU66HASXBQ/
- https://nvd.nist.gov/vuln/detail/CVE-2024-5642
- https://security.netapp.com/advisory/ntap-20240726-0005/
