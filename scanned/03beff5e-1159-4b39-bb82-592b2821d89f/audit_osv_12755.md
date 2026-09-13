# [M] CVE-2018-14629

## Summary
Severity: Medium
Advisory: CVE-2018-14629
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-14629
Type: osv

## Details
A denial of service vulnerability was discovered in Samba's LDAP server before versions 4.7.12, 4.8.7, and 4.9.3. A CNAME loop could lead to infinite recursion in the server. An unprivileged local attacker could create such an entry, leading to denial of service.

## References
- http://www.securityfocus.com/bid/106022
- https://lists.debian.org/debian-lts-announce/2018/12/msg00005.html
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://usn.ubuntu.com/3827-1/
- https://usn.ubuntu.com/3827-2/
- https://www.debian.org/security/2018/dsa-4345
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14629
- https://www.samba.org/samba/security/CVE-2018-14629.html
