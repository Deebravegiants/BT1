# [C] CVE-2025-52461

## Summary
Severity: Critical
Advisory: CVE-2025-52461
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-52461
Type: osv

## Details
An out-of-bounds read vulnerability exists in the Nex parsing functionality of The Biosig Project libbiosig 3.9.0 and Master Branch (35a819fa). A specially crafted .nex file can lead to an information leak. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2238
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2238
