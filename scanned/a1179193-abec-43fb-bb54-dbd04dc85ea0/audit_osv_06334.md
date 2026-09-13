# [M] Use-after-free in "unicode_escape" decoder with error handler

## Summary
Severity: Medium
Advisory: BIT-libpython-2025-4516
Aliases: BIT-python-2025-4516, BIT-python-min-2025-4516, CVE-2025-4516, PSF-2025-4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libpython-2025-4516
Type: osv

## Affected
- Bitnami: `libpython` — affected >=3.13.0 <3.13.4

## Details
There is an issue in CPython when using `bytes.decode("unicode_escape", error="ignore|replace")`. If you are not using the "unicode_escape" encoding or an error handler your usage is not affected. To work-around this issue you may stop using the error= handler and instead wrap the bytes.decode() call in a try-except catching the DecodeError.

## References
- http://www.openwall.com/lists/oss-security/2025/05/16/4
- http://www.openwall.com/lists/oss-security/2025/05/19/1
- https://github.com/python/cpython/commit/4398b788ffc1f954a2c552da285477d42a571292
- https://github.com/python/cpython/commit/6279eb8c076d89d3739a6edb393e43c7929b429d
- https://github.com/python/cpython/commit/69b4387f78f413e8c47572a85b3478c47eba8142
- https://github.com/python/cpython/commit/73b3040f592436385007918887b7e2132aa8431f
- https://github.com/python/cpython/commit/8d35fd1b34935221aff23a1ab69a429dd156be77
- https://github.com/python/cpython/commit/9f69a58623bd01349a18ba0c7a9cb1dad6a51e8e
- https://github.com/python/cpython/commit/ab9893c40609935e0d40a6d2a7307ea51aec598b
- https://github.com/python/cpython/issues/133767
- https://github.com/python/cpython/pull/129648
- https://mail.python.org/archives/list/security-announce@python.org/thread/L75IPBBTSCYEF56I2M4KIW353BB3AY74/
- https://nvd.nist.gov/vuln/detail/CVE-2025-4516
