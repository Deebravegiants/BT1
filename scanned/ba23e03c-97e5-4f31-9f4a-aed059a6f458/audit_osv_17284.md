# [M] CVE-2020-14323

## Summary
Severity: Medium
Advisory: CVE-2020-14323
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-29
Source: https://osv.dev/vulnerability/CVE-2020-14323
Type: osv

## Details
A null pointer dereference flaw was found in samba's Winbind service in versions before 4.11.15, before 4.12.9 and before 4.13.1. A local user could use this flaw to crash the winbind service causing denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/JE2M4FE3N3EDXVG4UKSVFPL7SQUGFFDP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/W6HM73N4NEGFW5GIJJGGP6ZZBS6GTXPB/
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2020-11/msg00012.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00041.html
- https://security.gentoo.org/glsa/202012-24
- https://security.netapp.com/advisory/ntap-20201103-0001/
- https://www.samba.org/samba/security/CVE-2020-14323.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1891685
