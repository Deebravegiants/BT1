# [M] ALPINE-CVE-2025-46803

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-46803
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-46803
Type: osv

## Affected
- Alpine:v3.21: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.22: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.23: `screen` — affected >=0 <5.0.1-r0
- Alpine:v3.24: `screen` — affected >=0 <5.0.1-r0

## Details
The default mode of pseudo terminals (PTYs) allocated by Screen was changed from 0620 to 0622, thereby allowing anyone to write to any Screen PTYs in the system.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-46803
