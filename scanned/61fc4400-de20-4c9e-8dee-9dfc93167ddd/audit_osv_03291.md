# [M] ALPINE-CVE-2025-46805

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-46805
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46805
Type: osv

## Affected
- Alpine:v3.18: `screen` — affected >=0 <4.9.1_git20250512-r0
- Alpine:v3.19: `screen` — affected >=0 <4.9.1_git20250512-r0
- Alpine:v3.20: `screen` — affected >=0 <4.9.1_git20250512-r0
- Alpine:v3.21: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.22: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.23: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.24: `screen` — affected >=0 <5.0.1-r0

## Details
Screen version 5.0.0 and older version 4 releases have  a TOCTOU race potentially allowing to send SIGHUP, SIGCONT to privileged processes when installed setuid-root.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46805
