# [M] ALPINE-CVE-2023-24626

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-24626
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-24626
Type: osv

## Affected
- Alpine:v3.15: `screen` — affected >=0 <4.8.0-r6
- Alpine:v3.16: `screen` — affected >=0 <4.9.0-r1
- Alpine:v3.17: `screen` — affected >=0 <4.9.0-r1
- Alpine:v3.18: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.19: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.20: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.21: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.22: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.23: `screen` — affected >=0 <4.9.0-r3
- Alpine:v3.24: `screen` — affected >=0 <4.9.0-r3

## Details
socket.c in GNU Screen through 4.9.0, when installed setuid or setgid (the default on platforms such as Arch Linux and FreeBSD), allows local users to send a privileged SIGHUP signal to any PID, causing a denial of service or disruption of the target process.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-24626
