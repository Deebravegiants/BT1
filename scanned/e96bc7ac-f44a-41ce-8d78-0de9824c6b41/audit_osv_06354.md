# [M] Tarfile.extract() doesn't fully respect filter parameter

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-4360
Aliases: BIT-python-2026-4360, BIT-python-min-2026-4360, CVE-2026-4360, PSF-2026-32
Ecosystem: Bitnami
Published: 2026-07-08
Source: https://osv.dev/vulnerability/BIT-libpython-2026-4360
Type: osv

## Affected
- Bitnami: `libpython` — affected unspecified

## Details
In the Tarfile.extract() function, the filter parameter is not passed properly when extracting hardlinks. An affected system that extracts content from untrusted tar files could end up writing files with an unexpected uid/gid despite the user passing filter='data' to the extract() function.

## References
- https://github.com/python/cpython/commit/5e0ef3f1afe892e4f64eb83368db57ac4c40cba0
- https://github.com/python/cpython/commit/7b57e8d51446297b8c7c482d224bc5f1938e4301
- https://github.com/python/cpython/commit/7ccdbaba2c54250a70d7f25632152df7655a5e0a
- https://github.com/python/cpython/commit/d2b2f5eacab4dd48446b63340613b05dcbbf0b44
- https://github.com/python/cpython/commit/eee3ddf0ca10283cc7fea724aae9cd8665f8d15e
- https://github.com/python/cpython/issues/151987
- https://github.com/python/cpython/pull/151988
- https://mail.python.org/archives/list/security-announce@python.org/thread/TWZW2PC2AZOV6FENIHFSRC63OM7MBGSB/
- https://nvd.nist.gov/vuln/detail/CVE-2026-4360
- https://github.com/python/cpython/commit/cf23b9153181062150d061468b6d24af33fe214f
- https://github.com/python/cpython/commit/0367912be336348b30572f8029cec4a282782d92
