# [H] CVE-2020-10704

## Summary
Severity: High
Advisory: CVE-2020-10704
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-05-06
Source: https://osv.dev/vulnerability/CVE-2020-10704
Type: osv

## Details
A flaw was found when using samba as an Active Directory Domain Controller. Due to the way samba handles certain requests as an Active Directory Domain Controller LDAP server, an unauthorized user can cause a stack overflow leading to a denial of service. The highest threat from this vulnerability is to system availability. This issue affects all samba versions before 4.10.15, before 4.11.8 and before 4.12.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U5KW3ZO35NVDO57JSBZHTQZOS3AIQ5QE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y7DVGCHG3XPIBQ5ETGMGW7MXNOO4HFH4/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00002.html
- https://lists.debian.org/debian-lts-announce/2020/11/msg00041.html
- https://security.gentoo.org/glsa/202007-15
- https://www.samba.org/samba/security/CVE-2020-10704.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10704
