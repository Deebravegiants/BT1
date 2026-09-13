# [H] Excessive read buffering DoS in http.client

## Summary
Severity: High
Advisory: BIT-libpython-2025-13836
Aliases: BIT-python-2025-13836, BIT-python-min-2025-13836, CVE-2025-13836, PSF-2025-14
Ecosystem: Bitnami
Published: 2026-05-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-13836
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.1

## Details
When reading an HTTP response from a server, if no read amount is specified, the default behavior will be to use Content-Length. This allows a malicious server to cause the client to read large amounts of data into memory, potentially causing OOM or other DoS.

## References
- https://github.com/python/cpython/commit/14b1fdb0a94b96f86fc7b86671ea9582b8676628
- https://github.com/python/cpython/commit/289f29b0fe38baf2d7cb5854f4bb573cc34a6a15
- https://github.com/python/cpython/commit/4ce27904b597c77d74dd93f2c912676021a99155
- https://github.com/python/cpython/commit/5a4c4a033a4a54481be6870aa1896fad732555b5
- https://github.com/python/cpython/commit/5dc101675fd22918facbbe0fecdc821502beaaf0
- https://github.com/python/cpython/commit/afc40bdd3dd71f343fd9016f6d8eebbacbd6587c
- https://github.com/python/cpython/issues/119451
- https://github.com/python/cpython/pull/119454
- https://mail.python.org/archives/list/security-announce@python.org/thread/OQ6G7MKRQIS3OAREC3HNG3D2DPOU34XO/
- https://nvd.nist.gov/vuln/detail/CVE-2025-13836
