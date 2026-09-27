# [M] An issue was discovered in dbus >= 1.3.0 before 1.12.18

## Summary
Severity: Medium
Advisory: JLSEC-2025-18
Ecosystem: Julia
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-18
Type: osv

## Affected
- Julia: `Dbus_jll` — affected >=0 <1.14.10+0

## Details
An issue was discovered in dbus >= 1.3.0 before 1.12.18. The DBusServer in libdbus, as used in dbus-daemon, leaks file descriptors when a message exceeds the per-message file descriptor limit. A local attacker with access to the D-Bus system bus or another system service's private `AF_UNIX` socket could use this to make the system service reach its file descriptor limit, denying service to subsequent D-Bus clients.

## References
- http://packetstormsecurity.com/files/172840/D-Bus-File-Descriptor-Leak-Denial-Of-Service.html
- http://www.openwall.com/lists/oss-security/2020/06/04/3
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/294
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.10.30
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.12.18
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.13.16
- https://security.gentoo.org/glsa/202007-46
- https://securitylab.github.com/advisories/GHSL-2020-057-DBus-DoS-file-descriptor-leak
- https://usn.ubuntu.com/4398-1/
- https://usn.ubuntu.com/4398-2/
