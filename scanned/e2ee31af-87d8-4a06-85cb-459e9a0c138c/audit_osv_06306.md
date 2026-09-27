# [H] BIT-libpython-2023-41105

## Summary
Severity: High
Advisory: BIT-libpython-2023-41105
Aliases: BIT-python-2023-41105, BIT-python-min-2023-41105, CVE-2023-41105, PSF-2023-9
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-41105
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.11.0 <3.11.5

## Details
An issue was discovered in Python 3.11 through 3.11.4. If a path containing '\0' bytes is passed to os.path.normpath(), the path will be truncated unexpectedly at the first '\0' byte. There are plausible cases in which an application would have rejected a filename for security reasons in Python 3.10.x or earlier, but that filename is no longer rejected in Python 3.11.x.

## References
- https://github.com/python/cpython/issues/106242
- https://github.com/python/cpython/pull/107981
- https://github.com/python/cpython/pull/107982
- https://github.com/python/cpython/pull/107983
- https://mail.python.org/archives/list/security-announce%40python.org/thread/D6CDW3ZZC5D444YGL3VQUY6D4ECMCQLD/
- https://nvd.nist.gov/vuln/detail/CVE-2023-41105
- https://security.netapp.com/advisory/ntap-20231006-0015/
