# [H] CVE-2020-12050

## Summary
Severity: High
Advisory: CVE-2020-12050
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-30
Source: https://osv.dev/vulnerability/CVE-2020-12050
Type: osv

## Details
SQLiteODBC 0.9996, as packaged for certain Linux distributions as 0.9996-4, has a race condition leading to root privilege escalation because any user can replace a /tmp/sqliteodbc$$ file with new contents that cause loading of an arbitrary library.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PR6B33IGBADGYDBTEEU36OGERER2HOGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PDS5RK7F47BRXHUYRWGMGLYU2GJEVZQA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WXPHBDVB3LAQUQJCZ4WIS3JWM7JFR56X/
- https://sysdream.com/news/lab/2020-05-25-cve-2020-12050-fedora-red-hat-centos-local-privilege-escalation-through-a-race-condition-in-the-sqliteodbc-installer-script/
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00013.html
- https://sysdream.com/news/lab/
- http://www.ch-werner.de/sqliteodbc/
- https://bugzilla.redhat.com/show_bug.cgi?id=1825762
