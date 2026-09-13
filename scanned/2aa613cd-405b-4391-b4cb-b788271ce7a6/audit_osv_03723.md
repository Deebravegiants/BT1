# [H] ALPINE-CVE-2026-43619

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-43619
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:P/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-43619
Type: osv

## Affected
- Alpine:v3.20: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.21: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.4.3-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.4.3-r0

## Details
Rsync version 3.4.2 and prior contain symlink race condition vulnerabilities in path-based system calls including chmod, lchown, utimes, rename, unlink, mkdir, symlink, mknod, link, rmdir, and lstat that allow local attackers to redirect operations to files outside the exported rsync module. Attackers with local filesystem access can exploit the timing window between path resolution and syscall execution by swapping symlinks to apply sender-supplied permissions, ownership, timestamps, or filenames to arbitrary files outside the intended module boundary on rsync daemons configured with 'use chroot = no'.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-43619
