# [H] BIT-libpython-2020-15523

## Summary
Severity: High
Advisory: BIT-libpython-2020-15523
Aliases: BIT-python-2020-15523, BIT-python-min-2020-15523, CVE-2020-15523, PSF-2020-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2020-15523
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.8.0 <3.8.4

## Details
In Python 3.6 through 3.6.10, 3.7 through 3.7.8, 3.8 through 3.8.4, and 3.9 through 3.9.0 on Windows, a Trojan horse python3.dll might be used in cases where CPython is embedded in a native application. This occurs because python3X.dll may use an invalid search path for python3.dll loading (after Py_SetPath has been used). NOTE: this issue CANNOT occur when using python.exe from a standard (non-embedded) Python installation on Windows.

## References
- https://bugs.python.org/issue29778
- https://github.com/python/cpython/pull/21297
- https://nvd.nist.gov/vuln/detail/CVE-2020-15523
- https://security.netapp.com/advisory/ntap-20210312-0004/
