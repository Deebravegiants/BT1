# [C] Code execution in Embedchain

## Summary
Severity: Critical
Advisory: GHSA-rhhj-5436-95vf
CVE: CVE-2024-23731
CWE: CWE-88, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-21
Source: https://github.com/advisories/GHSA-rhhj-5436-95vf
Type: github-advisory

## Affected
- PyPI: `embedchain` — affected >=0 <0.1.57

## Details
The OpenAPI loader in Embedchain before 0.1.57 allows attackers to execute arbitrary code, related to the openapi.py yaml.load function argument.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23731
- https://github.com/embedchain/embedchain/pull/1122
- https://github.com/embedchain/embedchain
- https://github.com/embedchain/embedchain/compare/0.1.56...0.1.57
- https://github.com/pypa/advisory-database/tree/main/vulns/embedchain/PYSEC-2024-7.yaml
