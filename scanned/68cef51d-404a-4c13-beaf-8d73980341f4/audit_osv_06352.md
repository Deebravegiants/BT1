# [M] Base64 decoding stops at first padded quad by default

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-3446
Aliases: BIT-python-2026-3446, BIT-python-min-2026-3446, CVE-2026-3446, PSF-2026-16
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-libpython-2026-3446
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.4

## Details
When calling base64.b64decode() or related functions the decoding process would stop after encountering the first padded quad regardless of whether there was more information to be processed. This can lead to data being accepted which may be processed differently by other implementations. Use "validate=True" to enable stricter processing of base64 data.

## References
- https://github.com/python/cpython/commit/1f9958f909c1b41a4ffc0b613ef8ec8fa5e7c474
- https://github.com/python/cpython/commit/4561f6418a691b3e89aef0901f53fe0dfb7f7c0e
- https://github.com/python/cpython/commit/e31c55121620189a0d1a07b689762d8ca9c1b7fa
- https://github.com/python/cpython/issues/145264
- https://github.com/python/cpython/pull/145267
- https://mail.python.org/archives/list/security-announce@python.org/thread/F5ZT5ICGJ6CKXVUJ34YBVY7WOZ5SHG53/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3446
