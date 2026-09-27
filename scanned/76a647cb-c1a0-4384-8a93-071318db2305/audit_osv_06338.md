# [H] Tarfile infinite loop during parsing with negative member offset

## Summary
Severity: High
Advisory: BIT-libpython-2025-8194
Aliases: BIT-python-2025-8194, BIT-python-min-2025-8194, CVE-2025-8194, PSF-2025-11
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-8194
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.6

## Details
There is a defect in the CPython “tarfile” module affecting the “TarFile” extraction and entry enumeration APIs. The tar implementation would process tar archives with negative offsets without error, resulting in an infinite loop and deadlock during the parsing of maliciously crafted tar archives. 

This vulnerability can be mitigated by including the following patch after importing the “tarfile” module:  https://gist.github.com/sethmlarson/1716ac5b82b73dbcbf23ad2eff8b33e1

## References
- https://gist.github.com/sethmlarson/1716ac5b82b73dbcbf23ad2eff8b33e1
- https://github.com/python/cpython/commit/7040aa54f14676938970e10c5f74ea93cd56aa38
- https://github.com/python/cpython/commit/c9d9f78feb1467e73fd29356c040bde1c104f29f
- https://github.com/python/cpython/commit/cdae923ffe187d6ef916c0f665a31249619193fe
- https://github.com/python/cpython/commit/fbc2a0ca9ac8aff6887f8ddf79b87b4510277227
- https://github.com/python/cpython/issues/130577
- https://github.com/python/cpython/pull/137027
- https://mail.python.org/archives/list/security-announce@python.org/thread/ZULLF3IZ726XP5EY7XJ7YIN3K5MDYR2D/
- https://nvd.nist.gov/vuln/detail/CVE-2025-8194
- https://github.com/python/cpython/commit/57f5981d6260ed21266e0c26951b8564cc252bc2
- https://github.com/python/cpython/commit/73f03e4808206f71eb6b92c579505a220942ef19
- https://github.com/python/cpython/commit/b4ec17488eedec36d3c05fec127df71c0071f6cb
- http://www.openwall.com/lists/oss-security/2025/07/28/1
- http://www.openwall.com/lists/oss-security/2025/07/28/2
- https://github.com/python/cpython/pull/57f5981d6260ed21266e0c26951b8564cc252bc2
- https://github.com/python/cpython/pull/73f03e4808206f71eb6b92c579505a220942ef19
- https://github.com/python/cpython/pull/b4ec17488eedec36d3c05fec127df71c0071f6cb
- https://github.com/python/cpython/pull/c9d9f78feb1467e73fd29356c040bde1c104f29f
- https://github.com/python/cpython/pull/cdae923ffe187d6ef916c0f665a31249619193fe
- https://github.com/python/cpython/pull/fbc2a0ca9ac8aff6887f8ddf79b87b4510277227
