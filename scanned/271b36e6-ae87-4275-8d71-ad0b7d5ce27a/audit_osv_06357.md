# [M] BaseCookie.js_output() does not neutralize embedded characters

## Summary
Severity: Medium
Advisory: BIT-libpython-2026-6019
Aliases: BIT-python-2026-6019, BIT-python-min-2026-6019, CVE-2026-6019, PSF-2026-21
Ecosystem: Bitnami
Published: 2026-06-25
Source: https://osv.dev/vulnerability/BIT-libpython-2026-6019
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.14.0 <3.14.5

## Details
http.cookies.Morsel.js_output() returns an inline <script> snippet and only escapes " for JavaScript string context. It does not neutralize the HTML parser-sensitive sequence </script> inside the generated script element. Mitigation base64-encodes the cookie value to disallow escaping using cookie value.

## References
- https://github.com/python/cpython/commit/3c59b8b53fc75c7f9578d16fb8201ceb43e8f76c
- https://github.com/python/cpython/commit/76b3923d688c0efc580658476c5f525ec8735104
- https://github.com/python/cpython/commit/f795e042043dfe26c42e1971d4502c1cdc4c65b8
- https://github.com/python/cpython/issues/90309
- https://github.com/python/cpython/pull/148848
- https://mail.python.org/archives/list/security-announce@python.org/thread/IVNWGV2BBNC3RHQAFS22UP4DY56SAXX3/
- https://nvd.nist.gov/vuln/detail/CVE-2026-6019
