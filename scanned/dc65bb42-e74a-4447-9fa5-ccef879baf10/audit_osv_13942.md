# [M] CVE-2018-5729

## Summary
Severity: Medium
Advisory: CVE-2018-5729
CVSS: 4.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L)
Published: 2018-03-06
Source: https://osv.dev/vulnerability/CVE-2018-5729
Type: osv

## Details
MIT krb5 1.6 or later allows an authenticated kadmin with permission to add principals to an LDAP Kerberos database to cause a denial of service (NULL pointer dereference) or bypass a DN container check by supplying tagged data that is internal to the database module.

## References
- http://www.securitytracker.com/id/1042071
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2018:3071
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=891869
- https://lists.debian.org/debian-lts-announce/2019/01/msg00020.html
- https://lists.debian.org/debian-lts-announce/2021/09/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GK5T6JPMBHBPKS7HNGHYUUF4KKRMNSNU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OIFUL3CPM4S5TOXTTOCQ3CUZN6XCXUTR/
- https://bugzilla.redhat.com/show_bug.cgi?id=1551083
- https://github.com/krb5/krb5/commit/e1caf6fb74981da62039846931ebdffed71309d1
