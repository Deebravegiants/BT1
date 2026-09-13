# [H] bz2.BZ2Decompressor reuse after error can cause a stack buffer overflow

## Summary
Severity: High
Advisory: BIT-libpython-2026-9669
Aliases: BIT-python-2026-9669, BIT-python-min-2026-9669, CVE-2026-9669, PSF-2026-27
Ecosystem: Bitnami
Published: 2026-06-25
Source: https://osv.dev/vulnerability/BIT-libpython-2026-9669
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.6

## Details
bz2.BZ2Decompressor objects could be reused after a decompression error. If an application caught the resulting OSError and retried with the same decompressor, crafted input could cause the decompressor to resume from an invalid internal state and perform out-of-bounds writes to a stack buffer. This could crash the process when processing untrusted data.

## References
- http://www.openwall.com/lists/oss-security/2026/06/08/17
- https://github.com/python/cpython/commit/157a5df8cb5d82b33f918a7489e72ce95ceb12b6
- https://github.com/python/cpython/commit/5755d0f083949ff3c5bf3a37e673e24e306b036e
- https://github.com/python/cpython/commit/619a12b2e545391dc436b3af79dda22337382a6f
- https://github.com/python/cpython/commit/d3ca26983dfbccdf609f24ff5877dc3118e4702d
- https://github.com/python/cpython/issues/150599
- https://github.com/python/cpython/pull/150600
- https://mail.python.org/archives/list/security-announce@python.org/thread/DBJZETMGUIFK7DVUWMOXHD3Z6IX2QPSX/
- https://nvd.nist.gov/vuln/detail/CVE-2026-9669
- https://github.com/python/cpython/commit/938ec030e90c5e53f1faac6fab1643f14e4f4a79
- https://github.com/python/cpython/commit/1ba6135eae75ad8413413caeeedb56ae72320636
- https://github.com/python/cpython/commit/991e6cf86496718c4ef00b362d640e00cb5c85b2
