# [M] ALPINE-CVE-2022-42012

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42012
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42012
Type: osv

## Affected
- Alpine:v3.13: `dbus` — affected >=1.13.0 <1.12.24-r0
- Alpine:v3.14: `dbus` — affected >=1.13.0 <1.12.24-r0
- Alpine:v3.15: `dbus` — affected >=1.13.0 <1.12.24-r0
- Alpine:v3.16: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.17: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.18: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.19: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.20: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.21: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.22: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.23: `dbus` — affected >=1.13.0 <1.14.4-r0
- Alpine:v3.24: `dbus` — affected >=1.13.0 <1.14.4-r0

## Details
An issue was discovered in D-Bus before 1.12.24, 1.13.x and 1.14.x before 1.14.4, and 1.15.x before 1.15.2. An authenticated attacker can cause dbus-daemon and other programs that use libdbus to crash by sending a message with attached file descriptors in an unexpected format.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42012
