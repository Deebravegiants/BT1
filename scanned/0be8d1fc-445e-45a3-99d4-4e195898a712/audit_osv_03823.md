# [H] ALPINE-CVE-2026-53799

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-53799
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-53799
Type: osv

## Affected
- Alpine:v3.21: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.22: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.23: `rsync` — affected >=0 <3.5.0-r0
- Alpine:v3.24: `rsync` — affected >=0 <3.5.0-r0

## Details
rsync before 3.5.0 contains a symlink race condition vulnerability that allows local attackers to cause rsync to apply arbitrary ACLs or extended attributes to unintended files by substituting a symlink at a predictable destination path between the file write and the subsequent acl_set_file() or lsetxattr() call. Attackers can exploit this timing window to redirect ACL and xattr application through a crafted symlink to files outside the intended destination tree, potentially granting elevated permissions and enabling local privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-53799
