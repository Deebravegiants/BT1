# [M] CVE-2018-10919

## Summary
Severity: Medium
Advisory: CVE-2018-10919
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-10919
Type: osv

## Details
The Samba Active Directory LDAP server was vulnerable to an information disclosure flaw because of missing access control checks. An authenticated attacker could use this flaw to extract confidential attribute values using LDAP search expressions. Samba versions before 4.6.16, 4.7.9 and 4.8.4 are vulnerable.

## References
- http://www.securityfocus.com/bid/105081
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20180814-0001/
- https://usn.ubuntu.com/3738-1/
- https://www.debian.org/security/2018/dsa-4271
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10919
- https://www.samba.org/samba/security/CVE-2018-10919.html
