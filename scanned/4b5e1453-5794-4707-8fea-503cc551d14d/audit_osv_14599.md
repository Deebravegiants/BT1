# [M] CVE-2019-10218

## Summary
Severity: Medium
Advisory: CVE-2019-10218
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2019-11-06
Source: https://osv.dev/vulnerability/CVE-2019-10218
Type: osv

## Details
A flaw was found in the samba client, all samba versions before samba 4.11.2, 4.10.10 and 4.9.15, where a malicious server can supply a pathname to the client with separators. This could allow the client to access files and folders outside of the SMB network pathnames. An attacker could use this vulnerability to create files outside of the current working directory using the privileges of the client user.

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00023.html
- https://lists.debian.org/debian-lts-announce/2023/09/msg00013.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/OKPYHDFI7HRELVXBE5J4MTGSI35AKFBI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UMIYCYXCPRTVCVZ3TP6ZGPJ6RZS3IX4G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/XQ3IUACPZJXSC4OM6P2V4IC4QMZQZWPD/
- http://lists.opensuse.org/opensuse-security-announce/2019-11/msg00015.html
- https://www.samba.org/samba/security/CVE-2019-10218.html
- https://www.synology.com/security/advisory/Synology_SA_19_35
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10218
