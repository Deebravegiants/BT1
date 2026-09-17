# [C] ALPINE-CVE-2026-73076

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-73076
Ecosystem: Alpine:v3.23
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-73076
Type: osv

## Affected
- Alpine:v3.23: `vim` — affected >=0 <9.2.0854-r0

## Details
Vim is an open source, command line text editor. Prior to 9.2.0847, runtime/autoload/vimball.vim allows a crafted vimball member named .VimballRecord to overwrite the installation record with attacker-chosen commands. When vimball#RmVimball() later processes the matching record entry, the stored Ex commands, including operating-system commands invoked through :!, execute with the privileges of the user running Vim. This issue is fixed in version 9.2.0847.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-73076
