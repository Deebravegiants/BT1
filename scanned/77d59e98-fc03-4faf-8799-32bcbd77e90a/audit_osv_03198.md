# [M] ALPINE-CVE-2025-15366

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-15366
Ecosystem: Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-01-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-15366
Type: osv

## Affected
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
The imaplib module, when passed a user-controlled command, can have additional commands injected using newlines. Mitigation rejects commands containing control characters.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-15366
