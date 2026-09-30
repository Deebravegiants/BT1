# [C] Directory traversal in zenml

## Summary
Severity: Critical
Advisory: GHSA-6h3f-43vq-53hj
CVE: CVE-2024-2083
CWE: CWE-29
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-16
Source: https://github.com/advisories/GHSA-6h3f-43vq-53hj
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0 <0.55.5

## Details
A directory traversal vulnerability exists in the zenml-io/zenml repository, specifically within the /api/v1/steps endpoint. Attackers can exploit this vulnerability by manipulating the 'logs' URI path in the request to fetch arbitrary file content, bypassing intended access restrictions. The vulnerability arises due to the lack of validation for directory traversal patterns, allowing attackers to access files outside of the restricted directory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2083
- https://github.com/zenml-io/zenml/commit/00e934f33a243a554f5f65b80eefd5ea5117367b
- https://github.com/pypa/advisory-database/tree/main/vulns/zenml/PYSEC-2024-247.yaml
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/f24b2216-6a4b-42a1-becb-9b47e6cf117f
