# [C] CVE-2025-66044

## Summary
Severity: Critical
Advisory: CVE-2025-66044
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-11
Source: https://osv.dev/vulnerability/CVE-2025-66044
Type: osv

## Details
Several stack-based buffer overflow vulnerabilities exists in the MFER parsing functionality of The Biosig Project libbiosig 3.9.1. A specially crafted MFER file can lead to arbitrary code execution. An attacker can provide a malicious file to trigger these vulnerabilities.When Tag is 64

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2025-2296
