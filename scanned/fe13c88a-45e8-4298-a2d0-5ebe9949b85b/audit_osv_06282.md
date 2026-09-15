# [C] BIT-libpython-2020-15801

## Summary
Severity: Critical
Advisory: BIT-libpython-2020-15801
Aliases: BIT-python-2020-15801, BIT-python-min-2020-15801, CVE-2020-15801
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2020-15801
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.8.0 <3.8.5

## Details
In Python 3.8.4, sys.path restrictions specified in a python38._pth file are ignored, allowing code to be loaded from arbitrary locations. The <executable-name>._pth file (e.g., the python._pth file) is not affected.

## References
- https://bugs.python.org/issue41304
- https://github.com/python/cpython/pull/21495
- https://nvd.nist.gov/vuln/detail/CVE-2020-15801
- https://security.netapp.com/advisory/ntap-20200731-0003/
