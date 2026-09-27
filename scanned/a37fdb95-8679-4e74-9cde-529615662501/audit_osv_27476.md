# [H] CVE-2024-22181

## Summary
Severity: High
Advisory: CVE-2024-22181
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-05-28
Source: https://osv.dev/vulnerability/CVE-2024-22181
Type: osv

## Details
An out-of-bounds write vulnerability exists in the readNODE functionality of libigl v2.5.0. A specially crafted .node file can lead to an out-of-bounds write. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1930
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1930
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22181.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22181
