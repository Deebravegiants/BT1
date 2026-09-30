# [M] Potential DoS via quadratic complexity in unicodedata.normalize()

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-3276
Aliases: BIT-python-2026-3276, BIT-python-min-2026-3276, CVE-2026-3276, PSF-2026-25
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-libpython-2026-3276
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.6

## Details
unicodedata.normalize() can take excessive CPU time when processing
specially crafted Unicode input containing long runs of combining characters
with alternating Canonical Combining Class values.
This affects all normalization forms.

## References
- http://www.openwall.com/lists/oss-security/2026/06/03/15
- https://github.com/python/cpython/commit/6b505d1f41f8f3ea0fe5a4786d3a8fff1875cfc0
- https://github.com/python/cpython/commit/991224b1e8311c85f198f6dd8208bf8cff7fc26f
- https://github.com/python/cpython/commit/ba785b88add96acbf403d65cb157fb2743a33a32
- https://github.com/python/cpython/commit/c5512bd7c1dc28055660565275012766941d3066
- https://github.com/python/cpython/issues/149079
- https://github.com/python/cpython/pull/149080
- https://mail.python.org/archives/list/security-announce@python.org/thread/PP5HB4K7727OBBM76KA2ILID76K3OZGZ/
- https://nvd.nist.gov/vuln/detail/CVE-2026-3276
- https://github.com/python/cpython/commit/90748760d38ca3ac5fc6788a69becab905c95598
- https://github.com/python/cpython/commit/d3ab945af25b28dfe13ac6cb40c124a01b33ce1f
- https://github.com/python/cpython/commit/db744c0776c1d5dd11aaa70eff2a6993c408bacc
- https://github.com/python/cpython/commit/e322a1857084d521f79f45181b776f62e6acfc2c
