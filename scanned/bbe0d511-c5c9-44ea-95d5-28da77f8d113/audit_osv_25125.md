# [M] CVE-2023-31194

## Summary
Severity: Medium
Advisory: CVE-2023-31194
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-31194
Type: osv

## Details
An improper array index validation vulnerability exists in the GraphPlanar::Write functionality of Diagon v1.0.139. A specially crafted markdown file can lead to memory corruption. A victim would need to open a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1745
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1745
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31194.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31194
