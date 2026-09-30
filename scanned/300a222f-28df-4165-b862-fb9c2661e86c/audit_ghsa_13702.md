# [H] upydev has weak encryption padding

## Summary
Severity: High
Advisory: GHSA-qc4j-hrj6-cppf
CVE: CVE-2023-48051
CWE: CWE-326
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-11-21
Source: https://github.com/advisories/GHSA-qc4j-hrj6-cppf
Type: github-advisory

## Affected
- PyPI: `upydev` — affected >=0

## Details
An issue in `/upydev/keygen.py` in upydev v0.4.3 allows attackers to decrypt sensitive information via weak encryption padding.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48051
- https://github.com/Carglglz/upydev/issues/38
- https://github.com/Carglglz/upydev
- https://github.com/pypa/advisory-database/tree/main/vulns/upydev/PYSEC-2023-302.yaml
