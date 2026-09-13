# [M] D-Bus before 1.15.6 sometimes allows unprivileged users to crash dbus-daemon

## Summary
Severity: Medium
Advisory: JLSEC-2025-22
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-22
Type: osv

## Affected
- Julia: `Dbus_jll` — affected >=0 <1.14.10+0

## Details
D-Bus before 1.15.6 sometimes allows unprivileged users to crash dbus-daemon. If a privileged user with control over the dbus-daemon is using the org.freedesktop.DBus.Monitoring interface to monitor message bus traffic, then an unprivileged user with the ability to connect to the same dbus-daemon can cause a dbus-daemon crash under some circumstances via an unreplyable message. When done on the well-known system bus, this is a denial-of-service vulnerability. The fixed versions are 1.12.28, 1.14.8, and 1.15.6.

## References
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/457
- https://lists.debian.org/debian-lts-announce/2023/10/msg00033.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZYCDRMD7B4XO4HF6C6YTLH4YUD7TANP/
- https://security.netapp.com/advisory/ntap-20231208-0007/
