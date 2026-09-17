# [H] CVE-2018-1057

## Summary
Severity: High
Advisory: CVE-2018-1057
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1057
Type: osv

## Details
On a Samba 4 AD DC the LDAP server in all versions of Samba from 4.0.0 onwards incorrectly validates permissions to modify passwords over LDAP allowing authenticated users to change any other users' passwords, including administrative users and privileged service accounts (eg Domain Controllers).

## References
- http://www.securityfocus.com/bid/103382
- http://www.securitytracker.com/id/1040494
- https://lists.debian.org/debian-lts-announce/2019/04/msg00013.html
- https://security.gentoo.org/glsa/201805-07
- https://security.netapp.com/advisory/ntap-20180313-0001/
- https://usn.ubuntu.com/3595-1/
- https://www.debian.org/security/2018/dsa-4135
- https://www.samba.org/samba/security/CVE-2018-1057.html
- https://www.synology.com/support/security/Synology_SA_18_08
- https://bugzilla.redhat.com/show_bug.cgi?id=1553553
