# [H] Missing SSL certificate validation in localstack

## Summary
Severity: High
Advisory: GHSA-8633-g3ph-97rp
CVE: CVE-2023-48054
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-16
Source: https://github.com/advisories/GHSA-8633-g3ph-97rp
Type: github-advisory

## Affected
- PyPI: `localstack` — affected >=0

## Details
Missing SSL certificate validation in localstack allows attackers to eavesdrop on communications between the host and server via a man-in-the-middle attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-48054
- https://github.com/localstack/localstack
- https://github.com/pypa/advisory-database/tree/main/vulns/localstack/PYSEC-2023-243.yaml
- https://gxx777.github.io/localstack_v_2.3.2_Cryptographic_API_Misuse_Vulnerability.md
