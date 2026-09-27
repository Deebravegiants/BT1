# [M] ALPINE-CVE-2026-53801

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-53801
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53801
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability in the sender's directory scanning logic that allows attackers to cause the sender to enumerate and transfer files outside the module root's intended subtree. Attackers who can create or manipulate symlinks in a path component of the scanned tree can replace a symlink with a directory entry pointing outside the module root between the lstat() call and the subsequent opendir() call, exposing files beyond the intended root in both daemon-mode and non-daemon sender-side scanning.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53801
