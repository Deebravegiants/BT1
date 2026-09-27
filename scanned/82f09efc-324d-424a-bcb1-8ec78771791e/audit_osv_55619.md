# [H] CVE-2026-20777

## Summary
Severity: High
Advisory: CVE-2026-20777
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-20777
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the Nicolet WFT parsing functionality of The Biosig Project libbiosig 3.9.2 and Master Branch (db9a9a63). A specially crafted .wft file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2026-2362
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2026-2362
