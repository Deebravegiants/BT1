# [H] ADMesh improper array index validation

## Summary
Severity: High
Advisory: GHSA-v5hv-4pw3-q6h9
CVE: CVE-2022-38072
CWE: CWE-118, CWE-129
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-03
Source: https://github.com/advisories/GHSA-v5hv-4pw3-q6h9
Type: github-advisory

## Affected
- PyPI: `admesh` — affected >=0 <0.98.5

## Details
An improper array index validation vulnerability exists in the stl_fix_normal_directions functionality of ADMesh Master Commit 767a105 and v0.98.4. A specially-crafted stl file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38072
- https://github.com/admesh/admesh/commit/5fab257268a0ee6f832c18d72af89810a29fbd5f
- https://github.com/admesh/python-admesh
- https://github.com/pypa/advisory-database/tree/main/vulns/admesh/PYSEC-2023-263.yaml
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1594
