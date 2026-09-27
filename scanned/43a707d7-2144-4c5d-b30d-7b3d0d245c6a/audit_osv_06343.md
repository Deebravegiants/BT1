# [H] tarfile opened in streaming mode mishandles EOF

## Summary
Severity: High
Advisory: BIT-libpython-2026-11972
Aliases: BIT-python-2026-11972, BIT-python-min-2026-11972, CVE-2026-11972, PSF-2026-31
Ecosystem: Bitnami
Published: 2026-07-30
Source: https://osv.dev/vulnerability/BIT-libpython-2026-11972
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.7

## Details
When using the "tarfile" module with a file opened in "streaming mode" (mode="r|") the tarfile module did not properly handle EOF, making archive parsing take exponentially longer.

## References
- https://github.com/python/cpython/commit/3f031d431f80668e14f3bc066bbf4369cd9281b9
- https://github.com/python/cpython/commit/4ce6bf7c8aa7725828a38981c306f214c1f29365
- https://github.com/python/cpython/commit/7f0dc59c9a70f8f3b4da33d7c4a2ba552a7acc21
- https://github.com/python/cpython/commit/e86666c9dd256d52d0fbef6feb1ea4a51768fdec
- https://github.com/python/cpython/commit/eb63c0f94dfcbea7fda8eab6213818e134d67192
- https://github.com/python/cpython/commit/f50bf13566189c8d0ce5a814f33eff3d89951896
- https://github.com/python/cpython/issues/151981
- https://github.com/python/cpython/pull/151982
- https://mail.python.org/archives/list/security-announce@python.org/thread/AXPSKKTSRKXTTJULW3XSIC74WZNAAPPB/
- https://nvd.nist.gov/vuln/detail/CVE-2026-11972
- https://github.com/python/cpython/commit/f5e2776ff0383a902c12acf2b703e7e951fc8438
