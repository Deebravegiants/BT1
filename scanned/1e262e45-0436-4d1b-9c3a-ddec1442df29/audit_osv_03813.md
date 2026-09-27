# [H] ALPINE-CVE-2026-53784

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53784
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53784
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a path traversal vulnerability that allows remote clients to access files outside the intended module root when use chroot is disabled and the module root path or a component of it is a symlink. The daemon calls chdir() to the module root at session initialization without resolving symlinks via realpath() or equivalent, causing subsequent relative-path operations to reference files relative to the symlink target rather than the intended module root, enabling unauthorized file access.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53784
