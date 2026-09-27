# [M] ALPINE-CVE-2018-14665

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-14665
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.6 (CVSS:3.0/AV:P/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14665
Type: osv

## Affected
- Alpine:v3.10: `xorg-server` — affected >=0 <1.20.3-r0
- Alpine:v3.11: `xorg-server` — affected >=0 <1.20.3-r0
- Alpine:v3.12: `xorg-server` — affected >=0 <1.20.3-r0
- Alpine:v3.6: `xorg-server` — affected >=0 <1.19.5-r1
- Alpine:v3.7: `xorg-server` — affected >=0 <1.19.5-r1
- Alpine:v3.8: `xorg-server` — affected >=0 <1.19.6-r3
- Alpine:v3.9: `xorg-server` — affected >=0 <1.20.3-r0

## Details
A flaw was found in xorg-x11-server before 1.20.3. An incorrect permission check for -modulepath and -logfile options when starting Xorg. X server allows unprivileged users with the ability to log in to the system via physical console to escalate their privileges and run arbitrary code under root privileges.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14665
