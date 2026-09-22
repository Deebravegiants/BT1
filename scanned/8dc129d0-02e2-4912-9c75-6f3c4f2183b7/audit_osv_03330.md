# [C] ALPINE-CVE-2025-54518

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2025-54518
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-54518
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r8
- Alpine:v3.21: `xen` — affected >=0 <4.19.5-r3
- Alpine:v3.22: `xen` — affected >=0 <4.20.3-r3
- Alpine:v3.23: `xen` — affected >=0 <4.20.3-r3
- Alpine:v3.24: `xen` — affected >=0 <4.21.1-r4

## Details
Improper isolation of shared resources within the CPU operation cache on Zen 2-based products could allow an attacker to corrupt instructions executed at a different privilege level, potentially resulting in privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-54518
