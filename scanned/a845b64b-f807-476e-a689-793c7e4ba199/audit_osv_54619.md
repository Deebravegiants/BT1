# [C] CVE-2024-22097

## Summary
Severity: Critical
Advisory: CVE-2024-22097
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-22097
Type: osv

## Details
A double-free vulnerability exists in the BrainVision Header Parsing functionality of The Biosig Project libbiosig Master Branch (ab0ee111) and 2.5.0. A specially crafted .vdhr file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2024-1917
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OIRLGNQM33KAWVWP5RPMAPHWNP3IY5YW/
- https://talosintelligence.com/vulnerability_reports/TALOS-2024-1917
