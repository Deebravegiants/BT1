# [M] ALPINE-CVE-2022-1348

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-1348
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-05-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-1348
Type: osv

## Affected
- Alpine:v3.13: `logrotate` — affected >=3.17.0 <3.18.0-r2
- Alpine:v3.14: `logrotate` — affected >=3.17.0 <3.18.1-r2
- Alpine:v3.15: `logrotate` — affected >=3.17.0 <3.18.1-r2
- Alpine:v3.16: `logrotate` — affected >=3.17.0 <3.19.0-r1
- Alpine:v3.17: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.18: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.19: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.20: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.21: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.22: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.23: `logrotate` — affected >=3.17.0 <3.20.1-r0
- Alpine:v3.24: `logrotate` — affected >=3.17.0 <3.20.1-r0

## Details
A vulnerability was found in logrotate in how the state file is created. The state file is used to prevent parallel executions of multiple instances of logrotate by acquiring and releasing a file lock. When the state file does not exist, it is created with world-readable permission, allowing an unprivileged user to lock the state file, stopping any rotation. This flaw affects logrotate versions before 3.20.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-1348
