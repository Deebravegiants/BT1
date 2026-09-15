# [M] CVE-2023-34969

## Summary
Severity: Medium
Advisory: CVE-2023-34969
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-34969
Type: osv

## Details
D-Bus before 1.15.6 sometimes allows unprivileged users to crash dbus-daemon. If a privileged user with control over the dbus-daemon is using the org.freedesktop.DBus.Monitoring interface to monitor message bus traffic, then an unprivileged user with the ability to connect to the same dbus-daemon can cause a dbus-daemon crash under some circumstances via an unreplyable message. When done on the well-known system bus, this is a denial-of-service vulnerability. The fixed versions are 1.12.28, 1.14.8, and 1.15.6.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34969.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZYCDRMD7B4XO4HF6C6YTLH4YUD7TANP/
- https://nvd.nist.gov/vuln/detail/CVE-2023-34969
- https://security.netapp.com/advisory/ntap-20231208-0007/
- https://gitlab.freedesktop.org/dbus/dbus/-/issues/457
- https://lists.debian.org/debian-lts-announce/2023/10/msg00033.html
