# [M] ALPINE-CVE-2026-8328

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-8328
Ecosystem: Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-8328
Type: osv

## Affected
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
The ftpcp() function in Lib/ftplib.py was not updated when 
CVE-2021-4189 was fixed. While makepasv() was patched to replace 
server-supplied PASV host addresses with the actual peer address 
(getpeername()[0]), ftpcp() still calls parse227() directly and passes 
the raw attacker-controllable IP address and port to target.sendport(). This patch is related to CVE-2021-4189.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-8328
