# [M] CVE-2020-12049

## Summary
Severity: Medium
Advisory: CVE-2020-12049
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-08
Source: https://osv.dev/vulnerability/CVE-2020-12049
Type: osv

## Details
An issue was discovered in dbus >= 1.3.0 before 1.12.18. The DBusServer in libdbus, as used in dbus-daemon, leaks file descriptors when a message exceeds the per-message file descriptor limit. A local attacker with access to the D-Bus system bus or another system service's private AF_UNIX socket could use this to make the system service reach its file descriptor limit, denying service to subsequent D-Bus clients.

## References
- http://packetstormsecurity.com/files/172840/D-Bus-File-Descriptor-Leak-Denial-Of-Service.html
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.10.30
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.12.18
- https://gitlab.freedesktop.org/dbus/dbus/-/tags/dbus-1.13.16
- https://security.gentoo.org/glsa/202007-46
- https://usn.ubuntu.com/4398-1/
- https://usn.ubuntu.com/4398-2/
- http://www.openwall.com/lists/oss-security/2020/06/04/3
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/294
- https://securitylab.github.com/advisories/GHSL-2020-057-DBus-DoS-file-descriptor-leak
