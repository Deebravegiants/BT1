# [H] ALPINE-CVE-2026-53783

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53783
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53783
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a time-of-check to time-of-use (TOCTOU) race condition vulnerability in the rrsync restricted shell wrapper that allows authenticated clients to escape enforced directory restrictions by substituting a symlink for a path component after validation but before transfer processing. Attackers can additionally leverage unrestricted flags such as --copy-unsafe-links, -D, and --log-file through rrsync to read or write files outside the permitted directory subtree.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53783
