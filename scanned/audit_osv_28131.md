# [H] CVE-2024-28130

## Summary
Severity: High
Advisory: CVE-2024-28130
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-23
Source: https://osv.dev/vulnerability/CVE-2024-28130
Type: osv

## Details
An incorrect type conversion vulnerability exists in the DVPSSoftcopyVOI_PList::createFromImage functionality of OFFIS DCMTK 3.6.8. A specially crafted malformed file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2024/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00032.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1957
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1957
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28130.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-28130
