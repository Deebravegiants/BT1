# [M] CVE-2018-1140

## Summary
Severity: Medium
Advisory: CVE-2018-1140
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-22
Source: https://osv.dev/vulnerability/CVE-2018-1140
Type: osv

## Details
A missing input sanitization flaw was found in the implementation of LDP database used for the LDAP server. An attacker could use this flaw to cause a denial of service against a samba server, used as a Active Directory Domain Controller. All versions of Samba from 4.8.0 onwards are vulnerable

## References
- http://www.securityfocus.com/bid/105082
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20180814-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-1140
- https://bugzilla.samba.org/show_bug.cgi?id=13374
- https://www.samba.org/samba/security/CVE-2018-1140.html
