# [H] Incremental HTMLParser feed() allows CPU-exhaustion DoS via repeated unterminated markup declarations

## Summary
Severity: High
Advisory: BIT-libpython-2026-15308
Aliases: BIT-python-2026-15308, BIT-python-min-2026-15308, CVE-2026-15308, PSF-2026-33
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-libpython-2026-15308
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.7

## Details
The incremental HTML parser (html.parser.HTMLParser) allows for CPU
denial-of-service through repeated unterminated markup declarations when
processing uncontrolled data.

## References
- http://www.openwall.com/lists/oss-security/2026/07/09/4
- https://github.com/python/cpython/commit/07efb08123ba9367a7107325adb9d5626dca1ca9
- https://github.com/python/cpython/commit/1e7956f1a722df9aabc509c30f8fbdc3a2b4fdc7
- https://github.com/python/cpython/commit/785df8f743800661961528970f8598edcd291c14
- https://github.com/python/cpython/commit/7933f4bf7131aa4140750f9404f5de0aa2969ced
- https://github.com/python/cpython/commit/bcf98ddbc40ec9b3ee87da0124a5660b19b7e606
- https://github.com/python/cpython/commit/c2390b9376e35a701ed3acc597b8fc87546c9b00
- https://github.com/python/cpython/commit/e9f92ac0b298292e7ff998e52cb8ccacfb27a0bd
- https://github.com/python/cpython/issues/153030
- https://github.com/python/cpython/pull/153031
- https://mail.python.org/archives/list/security-announce@python.org/thread/F6453LWKSHKCTWFLCOURWPLETNUIW2Z5/
- https://nvd.nist.gov/vuln/detail/CVE-2026-15308
