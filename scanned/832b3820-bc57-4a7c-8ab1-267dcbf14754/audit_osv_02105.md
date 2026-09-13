# [H] ALPINE-CVE-2021-23240

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-23240
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-23240
Type: osv

## Affected
- Alpine:v3.10: `sudo` — affected >=1.9.0 <1.9.5p2-r0
- Alpine:v3.11: `sudo` — affected >=1.9.0 <1.9.5p2-r0
- Alpine:v3.12: `sudo` — affected >=1.9.0 <1.9.5-r0
- Alpine:v3.13: `sudo` — affected >=1.9.0 <1.9.5-r0
- Alpine:v3.14: `sudo` — affected >=1.9.0 <1.9.5-r0
- Alpine:v3.15: `sudo` — affected >=1.9.0 <1.9.5-r0

## Details
selinux_edit_copy_tfiles in sudoedit in Sudo before 1.9.5 allows a local unprivileged user to gain file ownership and escalate privileges by replacing a temporary file with a symlink to an arbitrary file target. This affects SELinux RBAC support in permissive mode. Machines without SELinux are not vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-23240
