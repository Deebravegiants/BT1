# [H] Stack overflow parsing XML with deeply nested DTD content models

## Summary
Severity: High
Advisory: BIT-libpython-2026-4224
Aliases: BIT-python-2026-4224, BIT-python-min-2026-4224, CVE-2026-4224, PSF-2026-12
Ecosystem: Bitnami
Published: 2026-05-20
Source: https://osv.dev/vulnerability/BIT-libpython-2026-4224
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.4

## Details
When an Expat parser with a registered ElementDeclHandler parses an inline
document type definition containing a deeply nested content model a C stack
overflow occurs.

## References
- http://www.openwall.com/lists/oss-security/2026/03/16/4
- https://github.com/python/cpython/commit/196edfb06a7458377d4d0f4b3cd41724c1f3bd4a
- https://github.com/python/cpython/commit/642865ddf4b232da1f3b1f7abcfa3254c4bfe785
- https://github.com/python/cpython/commit/af856a7177326ac25d9f66cc6dd28b554d914fee
- https://github.com/python/cpython/commit/e0a8a6da90597a924b300debe045cdb4628ee1f3
- https://github.com/python/cpython/commit/eb0e8be3a7e11b87d198a2c3af1ed0eccf532768
- https://github.com/python/cpython/issues/145986
- https://github.com/python/cpython/pull/145987
- https://mail.python.org/archives/list/security-announce@python.org/thread/5M7CGUW3XBRY7II4DK43KF7NQQ3TPZ6R/
- https://nvd.nist.gov/vuln/detail/CVE-2026-4224
- https://github.com/python/cpython/commit/24ce88b285f56ee11626cf5e472af3cd8cc7c621
