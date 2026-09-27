# [C] CVE-2023-49606

## Summary
Severity: Critical
Advisory: CVE-2023-49606
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2023-49606
Type: osv

## Details
A use-after-free vulnerability exists in the HTTP Connection Headers parsing in Tinyproxy 1.11.1 and Tinyproxy 1.10.0. A specially crafted HTTP header can trigger reuse of previously freed memory, which leads to memory corruption and could lead to remote code execution. An attacker needs to make an unauthenticated HTTP request to trigger this vulnerability.

## References
- http://www.openwall.com/lists/oss-security/2024/05/07/1
- https://lists.debian.org/debian-lts-announce/2024/09/msg00035.html
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1889
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1889
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49606.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-49606
