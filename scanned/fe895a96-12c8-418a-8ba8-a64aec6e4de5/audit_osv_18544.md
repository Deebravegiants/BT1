# [H] CVE-2020-28596

## Summary
Severity: High
Advisory: CVE-2020-28596
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-10
Source: https://osv.dev/vulnerability/CVE-2020-28596
Type: osv

## Details
A stack-based buffer overflow vulnerability exists in the Objparser::objparse() functionality of Prusa Research PrusaSlicer 2.2.0 and Master (commit 4b040b856). A specially crafted obj file can lead to code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2020-1220
