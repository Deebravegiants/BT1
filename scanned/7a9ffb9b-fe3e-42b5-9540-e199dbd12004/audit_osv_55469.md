# [C] CVE-2025-53853

## Summary
Severity: Critical
Advisory: CVE-2025-53853
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-53853
Type: osv

## Details
A heap-based buffer overflow vulnerability exists in the ISHNE parsing functionality of The Biosig Project libbiosig 3.9.0 and Master Branch (35a819fa). A specially crafted ISHNE ECG annotations file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2025-2232
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2232
