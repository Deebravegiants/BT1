# [H] CVE-2025-64736

## Summary
Severity: High
Advisory: CVE-2025-64736
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2025-64736
Type: osv

## Details
An out-of-bounds read vulnerability exists in the ABF parsing functionality of The Biosig Project libbiosig 3.9.2 and Master Branch (5462afb0). A specially crafted .abf file can lead to an information leak. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2323
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2323
