# [C] CVE-2023-27882

## Summary
Severity: Critical
Advisory: CVE-2023-27882
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-11-14
Source: https://osv.dev/vulnerability/CVE-2023-27882
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the HTTP Server form boundary functionality of Weston Embedded uC-HTTP v3.01.01. A specially crafted network packet can lead to code execution. An attacker can send a malicious packet to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2023-1733
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2023-1733
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27882.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27882
