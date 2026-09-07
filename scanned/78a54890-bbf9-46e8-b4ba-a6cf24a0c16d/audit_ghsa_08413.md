# [M] FPDI: Memory Exhaustion and Endless Loop in FPDI leads to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-2mgw-7q6p-8grg
CVE: CVE-2026-45802
CWE: CWE-400, CWE-770
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-2mgw-7q6p-8grg
Type: github-advisory

## Affected
- Packagist: `setasign/fpdi` — affected >=0 <2.6.7

## Details
### Impact
This is a significant Denial of Service (DoS) vulnerability. Any application that uses FPDI to process user-supplied PDF files is at risk. An attacker can upload a small, malicious PDF file that will cause the server-side script to crash due to memory exhaustion or a script time-out. Repeated attacks can lead to sustained service unavailability.

### Patches
Fixed as of version 2.6.7

### Workarounds
No.

### References
No.

## References
- https://github.com/Setasign/FPDI/security/advisories/GHSA-2mgw-7q6p-8grg
- https://nvd.nist.gov/vuln/detail/CVE-2026-45802
- https://github.com/Setasign/FPDI/commit/1695cfcc7e01fe844a7296b3de90855a3fa65be6
- https://github.com/Setasign/FPDI
- https://github.com/Setasign/FPDI/releases/tag/v2.6.7
