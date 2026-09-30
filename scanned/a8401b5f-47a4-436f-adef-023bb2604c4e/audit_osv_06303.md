# [M] BIT-libpython-2023-33595

## Summary
Severity: Medium
Advisory: BIT-libpython-2023-33595
Aliases: BIT-python-2023-33595, BIT-python-min-2023-33595, CVE-2023-33595, PSF-2023-3
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2023-33595
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.12.0-alpha0 <3.12.0-alpha8

## Details
CPython v3.12.0 alpha 7 was discovered to contain a heap use-after-free via the function ascii_decode at /Objects/unicodeobject.c.

## References
- https://github.com/python/cpython/issues/103824
- https://github.com/python/cpython/pull/103993/commits/c120bc2d354ca3d27d0c7a53bf65574ddaabaf3a
- https://nvd.nist.gov/vuln/detail/CVE-2023-33595
