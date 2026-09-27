# [M] HTMLParser quadratic complexity when processing malformed inputs

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-6069
Aliases: BIT-python-2025-6069, BIT-python-min-2025-6069, CVE-2025-6069, PSF-2025-10
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-6069
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.6

## Details
The html.parser.HTMLParser class had worse-case quadratic complexity when processing certain crafted malformed inputs potentially leading to amplified denial-of-service.

## References
- https://github.com/python/cpython/commit/4455cbabf991e202185a25a631af206f60bbc949
- https://github.com/python/cpython/commit/6eb6c5dbfb528bd07d77b60fd71fd05d81d45c41
- https://github.com/python/cpython/commit/8d1b3dfa09135affbbf27fb8babcf3c11415df49
- https://github.com/python/cpython/commit/ab0893fd5c579d9cea30841680e6d35fc478afb5
- https://github.com/python/cpython/commit/d851f8e258c7328814943e923a7df81bca15df4b
- https://github.com/python/cpython/commit/f3c6f882cddc8dc30320d2e73edf019e201394fc
- https://github.com/python/cpython/commit/fdc9d214c01cb4588f540cfa03726bbf2a33fc15
- https://github.com/python/cpython/issues/135462
- https://github.com/python/cpython/pull/135464
- https://mail.python.org/archives/list/security-announce@python.org/thread/K5PIYLR6EP3WR7ZOKKYQUWEDNQVUXOYM/
- https://nvd.nist.gov/vuln/detail/CVE-2025-6069
