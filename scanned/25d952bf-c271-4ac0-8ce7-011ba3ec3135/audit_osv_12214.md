# [M] CVE-2018-10918

## Summary
Severity: Medium
Advisory: CVE-2018-10918
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-10918
Type: osv

## Details
A null pointer dereference flaw was found in the way samba checked database outputs from the LDB database layer. An authenticated attacker could use this flaw to crash a samba server in an Active Directory Domain Controller configuration. Samba versions before 4.7.9 and 4.8.4 are vulnerable.

## References
- http://www.securityfocus.com/bid/105083
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20180814-0001/
- https://usn.ubuntu.com/3738-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10918
- https://www.samba.org/samba/security/CVE-2018-10918.html
