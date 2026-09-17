# [M] CVE-2019-12436

## Summary
Severity: Medium
Advisory: CVE-2019-12436
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-06-19
Source: https://osv.dev/vulnerability/CVE-2019-12436
Type: osv

## Details
Samba 4.10.x before 4.10.5 has a NULL pointer dereference, leading to an AD DC LDAP server Denial of Service. This is related to an attacker using the paged search control. The attacker must have directory read access in order to attempt an exploit.

## References
- http://www.securityfocus.com/bid/108823
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZQ3LCJNJ3ONHIRKDSKOTT6QGXALLCHVG/
- https://usn.ubuntu.com/4018-1/
- https://www.samba.org/samba/security/CVE-2019-12436.html
- https://www.synology.com/security/advisory/Synology_SA_19_27
