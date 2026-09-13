# [H] ALPINE-CVE-2026-4786

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-4786
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-04-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4786
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0

## Details
Mitgation of CVE-2026-4519 was incomplete. If the URL contained "%action" the mitigation could be bypassed for certain browser types the "webbrowser.open()" API could have commands injected into the underlying shell. See CVE-2026-4519 for details.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4786
