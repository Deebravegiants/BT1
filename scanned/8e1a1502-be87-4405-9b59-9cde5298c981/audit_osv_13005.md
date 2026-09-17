# [M] CVE-2018-16851

## Summary
Severity: Medium
Advisory: CVE-2018-16851
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-16851
Type: osv

## Details
Samba from version 4.0.0 and before versions 4.7.12, 4.8.7, 4.9.3 is vulnerable to a denial of service. During the processing of an LDAP search before Samba's AD DC returns the LDAP entries to the client, the entries are cached in a single memory object with a maximum size of 256MB. When this size is reached, the Samba process providing the LDAP service will follow the NULL pointer, terminating the process. There is no further vulnerability associated with this issue, merely a denial of service.

## References
- http://www.securityfocus.com/bid/106027
- https://lists.debian.org/debian-lts-announce/2018/12/msg00005.html
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://usn.ubuntu.com/3827-1/
- https://usn.ubuntu.com/3827-2/
- https://www.debian.org/security/2018/dsa-4345
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16851
- https://www.samba.org/samba/security/CVE-2018-16851.html
