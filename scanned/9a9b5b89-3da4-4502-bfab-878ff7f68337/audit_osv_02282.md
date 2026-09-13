# [M] ALPINE-CVE-2021-3995

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-3995
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-3995
Type: osv

## Affected
- Alpine:v3.12: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.13: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.14: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.15: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.16: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.17: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.18: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.19: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.20: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.21: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.22: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.23: `util-linux` — affected >=2.34 <2.37.3-r0
- Alpine:v3.24: `util-linux` — affected >=2.34 <2.37.3-r0

## Details
A logic error was found in the libmount library of util-linux in the function that allows an unprivileged user to unmount a FUSE filesystem. This flaw allows an unprivileged local attacker to unmount FUSE filesystems that belong to certain other users who have a UID that is a prefix of the UID of the attacker in its string form. An attacker may use this flaw to cause a denial of service to applications that use the affected filesystems.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-3995
