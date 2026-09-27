# [M] SourcelessFileLoader does not use io.open_code()

## Summary
Severity: Medium
Advisory: CVE-2026-2297
Aliases: PSF-2026-9
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-04
Source: https://osv.dev/vulnerability/CVE-2026-2297
Type: osv

## Details
The import hook in CPython that handles legacy *.pyc files (SourcelessFileLoader) is incorrectly handled in FileLoader (a base class) and so does not use io.open_code() to read the .pyc files. sys.audit handlers for this audit event therefore do not fire.

## References
- http://www.openwall.com/lists/oss-security/2026/03/05/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/2xxx/CVE-2026-2297.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-2297
- https://github.com/python/cpython/issues/145506
- https://github.com/python/cpython/commit/482d6f8bdba9da3725d272e8bb4a2d25fb6a603e
- https://github.com/python/cpython/commit/69ddd9bb2cc4bd69b1565647c18659c6a789ccd9
- https://github.com/python/cpython/commit/876858c9f65d9ab656c7fa639f268ce7856d89dd
- https://github.com/python/cpython/commit/a51b1b512de1d56b3714b65628a2eae2b07e535e
- https://github.com/python/cpython/commit/c70adad78caeeea33f92f560ecb93331ca11bf66
- https://github.com/python/cpython/commit/e58e9802b9bec5cdbf48fc9bf1da5f4fda482e86
- https://github.com/python/cpython/pull/145507
- https://github.com/python/cpython
