# [M] Cryptography vulnerable to buffer overflow if non-contiguous buffers were passed to APIs

## Summary
Severity: Medium
Advisory: GHSA-p423-j2cm-9vmq
CVE: CVE-2026-39892
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-p423-j2cm-9vmq
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=45.0.0 <46.0.7

## Details
If a non-contiguous buffer was passed to APIs which accepted Python buffers (e.g. `Hash.update()`), this could lead to buffer overflows. For example:

```python
h = Hash(SHA256())
b.update(buf[::-1])
```

would read past the end of the buffer on Python >3.11

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-p423-j2cm-9vmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39892
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2026-36.yaml
- http://www.openwall.com/lists/oss-security/2026/04/08/12
