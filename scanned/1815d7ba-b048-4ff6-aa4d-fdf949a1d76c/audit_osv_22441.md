# [C] CVE-2022-29496

## Summary
Severity: Critical
Advisory: CVE-2022-29496
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-06-17
Source: https://osv.dev/vulnerability/CVE-2022-29496
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the BlynkConsole.h runCommand functionality of Blynk -Library v1.0.1. A specially-crafted network request can lead to command execution. An attacker can send a network request to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2022-1524
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29496.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-29496
