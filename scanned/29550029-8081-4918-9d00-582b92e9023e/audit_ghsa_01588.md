# [H] RSA decryption vulnerable to Bleichenbacher timing vulnerability

## Summary
Severity: High
Advisory: GHSA-hggm-jpg3-v476
CVE: CVE-2020-25659
CWE: CWE-385
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-hggm-jpg3-v476
Type: github-advisory

## Affected
- PyPI: `cryptography` — affected >=0 <3.2

## Details
RSA decryption was vulnerable to Bleichenbacher timing vulnerabilities, which would impact people using RSA decryption in online scenarios. This is fixed in cryptography 3.2.

## References
- https://github.com/pyca/cryptography/security/advisories/GHSA-hggm-jpg3-v476
- https://nvd.nist.gov/vuln/detail/CVE-2020-25659
- https://github.com/pyca/cryptography/pull/5507
- https://github.com/pyca/cryptography/commit/58494b41d6ecb0f56b7c5f05d5f5e3ca0320d494
- https://github.com/advisories/GHSA-hggm-jpg3-v476
- https://github.com/pyca/cryptography
- https://github.com/pypa/advisory-database/tree/main/vulns/cryptography/PYSEC-2021-62.yaml
- https://pypi.org/project/cryptography
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://www.oracle.com/security-alerts/cpujul2022.html
