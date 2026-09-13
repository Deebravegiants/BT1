# [H] ALPINE-CVE-2019-12749

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-12749
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2019-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-12749
Type: osv

## Affected
- Alpine:v3.10: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.11: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.12: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.13: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.14: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.15: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.16: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.17: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.18: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.19: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.20: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.21: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.22: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.23: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.24: `dbus` — affected >=1.12.0 <1.12.16-r0
- Alpine:v3.7: `dbus` — affected >=1.12.0 <1.10.28-r0
- Alpine:v3.8: `dbus` — affected >=1.12.0 <1.10.28-r0
- Alpine:v3.9: `dbus` — affected >=1.12.0 <1.10.28-r0

## Details
dbus before 1.10.28, 1.12.x before 1.12.16, and 1.13.x before 1.13.12, as used in DBusServer in Canonical Upstart in Ubuntu 14.04 (and in some, less common, uses of dbus-daemon), allows cookie spoofing because of symlink mishandling in the reference implementation of DBUS_COOKIE_SHA1 in the libdbus library. (This only affects the DBUS_COOKIE_SHA1 authentication mechanism.) A malicious client with write access to its own home directory could manipulate a ~/.dbus-keyrings symlink to cause a DBusServer with a different uid to read and write in unintended locations. In the worst case, this could result in the DBusServer reusing a cookie that is known to the malicious client, and treating that cookie as evidence that a subsequent client connection came from an attacker-chosen uid, allowing authentication bypass.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-12749
