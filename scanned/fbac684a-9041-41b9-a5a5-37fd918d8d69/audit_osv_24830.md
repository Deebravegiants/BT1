# [H] CVE-2023-27390

## Summary
Severity: High
Advisory: CVE-2023-27390
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-27390
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the Sequence::DrawText functionality of Diagon v1.0.139. A specially crafted markdown file can lead to arbitrary code execution. A victim would need to open a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1744
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1744
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27390.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27390
