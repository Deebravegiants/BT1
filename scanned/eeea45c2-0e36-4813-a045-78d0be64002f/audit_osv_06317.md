# [H] Regular-expression DoS when parsing TarFile headers

## Summary
Severity: High
Advisory: BIT-libpython-2024-6232
Aliases: BIT-python-2024-6232, BIT-python-min-2024-6232, CVE-2024-6232, PSF-2024-11
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2024-6232
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0 <3.12.6

## Details
There is a MEDIUM severity vulnerability affecting CPython.





Regular expressions that allowed excessive backtracking during tarfile.TarFile header parsing are vulnerable to ReDoS via specifically-crafted tar archives.

## References
- http://www.openwall.com/lists/oss-security/2024/09/03/5
- https://github.com/python/cpython/commit/34ddb64d088dd7ccc321f6103d23153256caa5d4
- https://github.com/python/cpython/commit/4eaf4891c12589e3c7bdad5f5b076e4c8392dd06
- https://github.com/python/cpython/commit/743acbe872485dc18df4d8ab2dc7895187f062c4
- https://github.com/python/cpython/commit/7d1f50cd92ff7e10a1c15a8f591dde8a6843a64d
- https://github.com/python/cpython/commit/b4225ca91547aa97ed3aca391614afbb255bc877
- https://github.com/python/cpython/commit/d449caf8a179e3b954268b3a88eb9170be3c8fbf
- https://github.com/python/cpython/commit/ed3a49ea734ada357ff4442996fd4ae71d253373
- https://github.com/python/cpython/issues/121285
- https://github.com/python/cpython/pull/121286
- https://mail.python.org/archives/list/security-announce@python.org/thread/JRYFTPRHZRTLMZLWQEUHZSJXNHM4ACTY/
- https://nvd.nist.gov/vuln/detail/CVE-2024-6232
- https://security.netapp.com/advisory/ntap-20241018-0007/
- https://lists.debian.org/debian-lts-announce/2024/12/msg00000.html
