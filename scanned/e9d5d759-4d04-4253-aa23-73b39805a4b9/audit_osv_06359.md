# [H] The expat and elementtree parsers use insufficient entropy for XML hash-flooding protection

## Summary
Severity: High
Advisory: BIT-libpython-2026-7210
Aliases: BIT-python-2026-7210, BIT-python-min-2026-7210, CVE-2026-7210, PSF-2026-23
Ecosystem: Bitnami
Published: 2026-06-05
Source: https://osv.dev/vulnerability/BIT-libpython-2026-7210
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.6

## Details
`xml.parsers.expat` and `xml.etree.ElementTree` use insufficient entropy for Expat hash-flooding protection, which allows a crafted XML document to trigger hash flooding.\r\n\r\nFully mitigating this vulnerability requires both updating libexpat to 2.8.0 or later and applying this patch.

## References
- http://www.openwall.com/lists/oss-security/2026/05/11/13
- http://www.openwall.com/lists/oss-security/2026/05/11/8
- https://github.com/python/cpython/issues/149018
- https://github.com/python/cpython/pull/149023
- https://mail.python.org/archives/list/security-announce@python.org/thread/PNY5OMBDPM2FRUZTWFFPJ6LISWKV627K/
- https://nvd.nist.gov/vuln/detail/CVE-2026-7210
- https://github.com/python/cpython/commit/24b8f12544468e4cedf5bfbe25442fcd495391e4
- https://github.com/python/cpython/commit/3573b3b1ecbd99030a0b18658e1bfece771b2566
- https://github.com/python/cpython/commit/eeea765cb9d8f1fc3d8918b272ac3c477983f27a
- https://github.com/python/cpython/commit/fc9b11ff49cbc82e6f917d07a61517a2b5f3145f
- https://github.com/python/cpython/commit/cbaecf9f16da611a646d507c1cbca265c588fc56
- https://github.com/python/cpython/commit/e37df2a6a71d6538698e2d3188a7c345b827640b
- https://github.com/python/cpython/commit/ea70712d1a8508e14e9677d44f838dab04dc0286
