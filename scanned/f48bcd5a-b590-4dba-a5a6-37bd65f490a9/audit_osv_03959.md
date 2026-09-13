# [C] ALPINE-CVE-2026-76642

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-76642
Ecosystem: Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-76642
Type: osv

## Affected
- Alpine:v3.22: `util-linux` — affected >=0 <2.41.6-r0
- Alpine:v3.23: `util-linux` — affected >=0 <2.41.6-r0
- Alpine:v3.24: `util-linux` — affected >=0 <2.42.3-r0

## Details
util-linux versions through 2.41.5 and 2.42.2 fail to check mount helper exit status before running post-mount hooks, allowing unprivileged users to execute privileged operations on pre-existing filesystems. Attackers can exploit X-mount.idmap or X-mount.owner hooks to clone filesystems with inherited suid bits or modify target inode permissions after a helper fails, achieving privilege escalation.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-76642
