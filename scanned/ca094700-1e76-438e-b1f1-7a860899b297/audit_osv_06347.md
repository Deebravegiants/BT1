# [M] stringprep.map_table_b2() deviates from RFC 3454 Table B.2

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-17084
Aliases: BIT-python-2026-17084, BIT-python-min-2026-17084, CVE-2026-17084, PSF-2026-37
Ecosystem: Bitnami
Published: 2026-09-11
Source: https://osv.dev/vulnerability/BIT-libpython-2026-17084
Type: osv

## Affected
- Bitnami: `libpython` — affected unspecified

## Details
The "stringprep" module didn't process characters from RFC 3454 tables 
B.2 or B.3 correctly: the latest Unicode codepoint attributes were used 
instead of the specified Unicode 3.2.0. This behavior would cause 
mismatches when processing domain names using IDNA 2003 (the "idna" 
codec) and the in_table_b2() function of the "stringprep" module. This 
only affects domain names containing characters that were not previously
 registered or had their Unicode attributes such as case-folding 
behavior updated since Unicode 3.2.0.

## References
- http://www.openwall.com/lists/oss-security/2026/08/18/2
- https://github.com/python/cpython/commit/1e54caa096678a38afcabecabb1ff72400dd6bae
- https://github.com/python/cpython/commit/5181304bcec9cfc3c15311741c9154cdff2e3fd7
- https://github.com/python/cpython/commit/7e109d084d55e7eb25837a5f3b47ef9beee547bc
- https://github.com/python/cpython/commit/c016c2535b74227fddf2cf7334dbfead6c930214
- https://github.com/python/cpython/issues/155292
- https://github.com/python/cpython/pull/155293
- https://mail.python.org/archives/list/security-announce@python.org/thread/EUHHTC6EV7HCLSUHP25C5VHSV4V2MUZN/
- https://nvd.nist.gov/vuln/detail/CVE-2026-17084
- https://github.com/python/cpython/commit/c28b121a4f0b975937c8b5a1b4934bb361d84296
- https://github.com/python/cpython/commit/c42790b34f634051750e5da340d17c7da19e4784
