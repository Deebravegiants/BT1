# [H] CVE-2023-49600

## Summary
Severity: High
Advisory: CVE-2023-49600
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2023-49600
Type: osv

## Details
An out-of-bounds write vulnerability exists in the PlyFile ply_cast_ascii functionality of libigl v2.5.0. A specially crafted .ply file can lead to a heap buffer overflow. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1879
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1879
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49600.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49600
