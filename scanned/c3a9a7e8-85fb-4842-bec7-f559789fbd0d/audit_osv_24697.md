# [C] CVE-2023-25181

## Summary
Severity: Critical
Advisory: CVE-2023-25181
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-11-14
Source: https://osv.dev/vulnerability/CVE-2023-25181
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the HTTP Server functionality of Weston Embedded uC-HTTP v3.01.01. A specially crafted set of network packets can lead to arbitrary code execution. An attacker can send a malicious packet to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1726
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1726
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25181.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25181
