# [M] Folding email comments of unfoldable characters doesn't preserve parenthesis

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-11468
Aliases: BIT-python-2025-11468, BIT-python-min-2025-11468, CVE-2025-11468, PSF-2026-1
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-libpython-2025-11468
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.3

## Details
When folding a long comment in an email header containing exclusively unfoldable characters, the parenthesis would not be preserved. This could be used for injecting headers into email messages where addresses are user-controlled and not sanitized.

## References
- https://github.com/python/cpython/commit/17d1490aa97bd6b98a42b1a9b324ead84e7fd8a2
- https://github.com/python/cpython/issues/143935
- https://github.com/python/cpython/pull/143936
- https://mail.python.org/archives/list/security-announce@python.org/thread/FELSEOLBI2QR6YLG6Q7VYF7FWSGQTKLI/
- https://nvd.nist.gov/vuln/detail/CVE-2025-11468
- https://github.com/python/cpython/commit/61614a5e5056e4f61ced65008d4576f3df34acb6
- https://github.com/python/cpython/commit/e9970f077240c7c670e8a6fc6662f2b30d3b6ad0
- https://github.com/python/cpython/commit/f738386838021c762efea6c9802c82de65e87796
- https://github.com/python/cpython/commit/a76e4cd62dd68e7cbe86e37e6ed988495a646b66
- https://github.com/python/cpython/commit/003b8315669b9f08b1010a49071f73f15f818094
