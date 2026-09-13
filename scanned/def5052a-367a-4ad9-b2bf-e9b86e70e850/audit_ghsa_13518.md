# [C] Yamcs API Directory Traversal vulnerability

## Summary
Severity: Critical
Advisory: GHSA-43fw-536j-w37j
CVE: CVE-2023-45278
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-43fw-536j-w37j
Type: github-advisory

## Affected
- Maven: `org.yamcs:yamcs` — affected >=0 <5.8.7

## Details
Directory Traversal vulnerability in the storage functionality of the API in Yamcs 5.8.6 allows attackers to delete arbitrary files via crafted HTTP DELETE request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-45278
- https://github.com/yamcs/yamcs
- https://github.com/yamcs/yamcs/compare/yamcs-5.8.6...yamcs-5.8.7
- https://www.linkedin.com/pulse/yamcs-vulnerability-assessment-visionspace-technologies
