# [M] ALPINE-CVE-2020-12049

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-12049
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-12049
Type: osv

## Affected
- Alpine:v3.10: `dbus` — affected >=1.3.0 <1.12.16-r1
- Alpine:v3.11: `dbus` — affected >=1.3.0 <1.12.16-r3
- Alpine:v3.12: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.13: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.14: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.15: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.16: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.17: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.18: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.19: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.20: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.21: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.22: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.23: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.24: `dbus` — affected >=1.3.0 <1.12.18-r0
- Alpine:v3.9: `dbus` — affected >=1.3.0 <1.12.28-r1

## Details
An issue was discovered in dbus >= 1.3.0 before 1.12.18. The DBusServer in libdbus, as used in dbus-daemon, leaks file descriptors when a message exceeds the per-message file descriptor limit. A local attacker with access to the D-Bus system bus or another system service's private AF_UNIX socket could use this to make the system service reach its file descriptor limit, denying service to subsequent D-Bus clients.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-12049
