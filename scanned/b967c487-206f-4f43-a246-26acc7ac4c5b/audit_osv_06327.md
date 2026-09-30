# [M] Out-of-memory when loading Plist

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-13837
Aliases: BIT-python-2025-13837, BIT-python-min-2025-13837, CVE-2025-13837, PSF-2025-15
Ecosystem: Bitnami
Published: 2025-12-05
Source: https://osv.dev/vulnerability/BIT-libpython-2025-13837
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.1

## Details
When loading a plist file, the plistlib module reads data in size specified by the file itself, meaning a malicious file can cause OOM and DoS issues

## References
- https://github.com/python/cpython/commit/694922cf40aa3a28f898b5f5ee08b71b4922df70
- https://github.com/python/cpython/commit/71fa8eb8233b37f16c88b6e3e583b461b205d1ba
- https://github.com/python/cpython/commit/b64441e4852383645af5b435411a6f849dd1b4cb
- https://github.com/python/cpython/issues/119342
- https://github.com/python/cpython/pull/119343
- https://mail.python.org/archives/list/security-announce@python.org/thread/2X5IBCJXRQAZ5PSERLHMSJFBHFR3QM2C/
- https://nvd.nist.gov/vuln/detail/CVE-2025-13837
- https://github.com/python/cpython/commit/5a8b19677d818fb41ee55f310233772e15aa1a2b
- https://github.com/python/cpython/commit/568342cfc8f002d9a15f30238f26b9d2e0e79036
- https://github.com/python/cpython/commit/cefee7d118a26ef6cd43db59bb9d98ca9a331111
