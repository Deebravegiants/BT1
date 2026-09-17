# [H] ALPINE-CVE-2026-53785

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53785
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53785
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a path traversal vulnerability that allows a malicious sender to write files outside the intended destination directory tree by crafting relative paths with symlink components in --relative mode. The make_path() function follows symlinks pointing outside the destination tree while creating intermediate directories without verifying that created paths remain within the destination boundary, enabling arbitrary file writes on the receiver's filesystem.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53785
