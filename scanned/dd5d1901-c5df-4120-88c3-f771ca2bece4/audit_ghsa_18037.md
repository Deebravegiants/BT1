# [M] FPDI allows Memory Exhaustion (OOM) in PDF Parser which leads to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-jxhh-4648-vpp3
CVE: CVE-2025-54869
CWE: CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-05
Source: https://github.com/advisories/GHSA-jxhh-4648-vpp3
Type: github-advisory

## Affected
- Packagist: `setasign/fpdi` — affected >=0 <2.6.4

## Details
### Impact
This is a significant Denial of Service (DoS) vulnerability. Any application that uses FPDI to process
user-supplied PDF files is at risk. An attacker can upload a small, malicious PDF file that will cause
the server-side script to crash due to memory exhaustion. Repeated attacks can lead to sustained
service unavailability.

### Patches
Fixed as of version 2.6.4

### Workarounds
No.

## References
- https://github.com/Setasign/FPDI/security/advisories/GHSA-jxhh-4648-vpp3
- https://nvd.nist.gov/vuln/detail/CVE-2025-54869
- https://github.com/Setasign/FPDI/commit/ba671ba9221cffd32c2dda87316c19f522a1c5f0
- https://github.com/Setasign/FPDI
