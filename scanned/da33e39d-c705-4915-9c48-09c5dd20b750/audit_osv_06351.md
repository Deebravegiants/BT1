# [H] Out-of-bounds write in Windows asyncio.ProacterEventLoop.sock_recvfrom_into() when using nbytes

## Summary
Severity: High
Advisory: BIT-libpython-2026-3298
Aliases: BIT-python-2026-3298, BIT-python-min-2026-3298, CVE-2026-3298, PSF-0000-CVE-2026-3298, PSF-2026-20
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-libpython-2026-3298
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.5

## Details
The method "sock_recvfrom_into()" of "asyncio.ProacterEventLoop" (Windows only) was missing a boundary check for the data buffer when using nbytes parameter. This allowed for an out-of-bounds buffer write if data was larger than the buffer size. Non-Windows platforms are not affected.

## References
- https://github.com/python/cpython/commit/1274766d3c29007ab77245a72abbf8dce2a9db4d
- https://github.com/python/cpython/commit/27522b7d6e6588f03e61099dd858cd5a9314e2f2
- https://github.com/python/cpython/commit/95633d2aad4721e25e4dfd9f43dfb6e1edcbd741
- https://github.com/python/cpython/issues/148808
- https://github.com/python/cpython/pull/148809
- https://mail.python.org/archives/list/security-announce@python.org/thread/KWTPIQBOOOUNQP7UFSLBI437NJDFLA3F/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3298
- https://github.com/python/cpython/commit/6c8b85b3f1d83d5697ec19880960e1eacee56688
- https://github.com/python/cpython/commit/f5ca38739241fe7a40a4b116d5a8a1364dd6fea7
