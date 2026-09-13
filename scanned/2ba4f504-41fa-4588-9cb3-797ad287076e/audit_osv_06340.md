# [M] Header injection in http.cookies.Morsel

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-0672
Aliases: BIT-python-2026-0672, BIT-python-min-2026-0672, CVE-2026-0672, PSF-2026-5
Ecosystem: Bitnami
Published: 2026-01-26
Source: https://osv.dev/vulnerability/BIT-libpython-2026-0672
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.3

## Details
When using http.cookies.Morsel, user-controlled cookie values and parameters can allow injecting HTTP headers into messages. Patch rejects all control characters within cookie names, values, and parameters.

## References
- https://github.com/python/cpython/commit/712452e6f1d4b9f7f8c4c92ebfcaac1705faa440
- https://github.com/python/cpython/commit/95746b3a13a985787ef53b977129041971ed7f70
- https://github.com/python/cpython/issues/143919
- https://github.com/python/cpython/pull/143920
- https://mail.python.org/archives/list/security-announce@python.org/thread/6VFLQQEIX673KXKFUZXCUNE5AZOGZ45M/
- https://nvd.nist.gov/vuln/detail/CVE-2026-0672
- https://github.com/python/cpython/commit/62700107418eb2cca3fc88da036a243ea975f172
- https://github.com/python/cpython/commit/7852d72b653fea0199acf5fc2a84f6f8b84eba8d
- https://github.com/python/cpython/commit/918387e4912d12ffc166c8f2a38df92b6ec756ca
- https://github.com/python/cpython/commit/b1869ff648bbee0717221d09e6deff46617f3e85
