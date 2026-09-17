# [M] Out-of-bounds read/write during remote profiling and asyncio process introspection when connecting to malicious target

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-5713
Aliases: BIT-python-2026-5713, BIT-python-min-2026-5713, CVE-2026-5713, PSF-2026-19
Ecosystem: Bitnami
Published: 2026-07-08
Source: https://osv.dev/vulnerability/BIT-libpython-2026-5713
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.5

## Details
The "profiling.sampling" module (Python 3.15+) and "asyncio introspection capabilities" (3.14+, "python -m asyncio ps" and "python -m asyncio pstree") features could be used to read and write addresses in a privileged process if that process connected to a malicious or "infected" Python process via the remote debugging feature. This vulnerability requires persistently and repeatedly connecting to the process to be exploited, even after the connecting process crashes with high likelihood due to ASLR.

## References
- http://www.openwall.com/lists/oss-security/2026/04/15/6
- https://github.com/python/cpython/commit/289fd2c97a7e5aecb8b69f94f5e838ccfeee7e67
- https://github.com/python/cpython/commit/316f6265b7f9ca4ffed5346b747475ef1943f35d
- https://github.com/python/cpython/issues/148178
- https://github.com/python/cpython/pull/148187
- https://mail.python.org/archives/list/security-announce@python.org/thread/OG4RHARYSNIE22GGOMVMCRH76L5HKPLM/
- https://nvd.nist.gov/vuln/detail/CVE-2026-5713
