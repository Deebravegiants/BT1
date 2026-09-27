# [H] CVE-2020-10745

## Summary
Severity: High
Advisory: CVE-2020-10745
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-07-07
Source: https://osv.dev/vulnerability/CVE-2020-10745
Type: osv

## Details
A flaw was found in all Samba versions before 4.10.17, before 4.11.11 and before 4.12.4 in the way it processed NetBios over TCP/IP. This flaw allows a remote attacker could to cause the Samba server to consume excessive CPU use, resulting in a denial of service. This highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6YLNQ5GRXUKYRUAOFZ4DUBVN4SMTL6Q2/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00030.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00002.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00041.html
- https://security.gentoo.org/glsa/202007-15
- https://www.samba.org/samba/security/CVE-2020-10745.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1849491%3B
