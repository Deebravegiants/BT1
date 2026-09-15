# [M] ALPINE-CVE-2026-11972

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-11972
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-11972
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
When using the "tarfile" module with a file opened in "streaming mode" (mode="r|") the tarfile module did not properly handle EOF, making archive parsing take exponentially longer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-11972
