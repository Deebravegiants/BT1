# [M] Header injection via newlines in data URL mediatype

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-15282
Aliases: BIT-python-2025-15282, BIT-python-min-2025-15282, CVE-2025-15282, PSF-2026-2
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-libpython-2025-15282
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.3

## Details
User-controlled data URLs parsed by urllib.request.DataHandler allow injecting headers through newlines in the data URL mediatype.

## References
- https://github.com/python/cpython/commit/05356b1cc153108aaf27f3b72ce438af4aa218c0
- https://github.com/python/cpython/commit/f25509e78e8be6ea73c811ac2b8c928c28841b9f
- https://github.com/python/cpython/issues/143925
- https://github.com/python/cpython/pull/143926
- https://mail.python.org/archives/list/security-announce@python.org/thread/X66HL7SISGJT33J53OHXMZT4DFLMHVKF/
- https://nvd.nist.gov/vuln/detail/CVE-2025-15282
- https://github.com/python/cpython/commit/34d76b00dabde81a793bd06dd8ecb057838c4b38
- https://github.com/python/cpython/commit/3f396ca9d7bbe2a50ea6b8c9b27c0082884d9f80
- https://github.com/python/cpython/commit/4ed11d3cd288e6b90196a15c5a825a45d318fe47
- https://github.com/python/cpython/commit/a35ca3be5842505dab74dc0b90b89cde0405017a
