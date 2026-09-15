# [M] CVE-2020-10700

## Summary
Severity: Medium
Advisory: CVE-2020-10700
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2020-05-04
Source: https://osv.dev/vulnerability/CVE-2020-10700
Type: osv

## Details
A use-after-free flaw was found in the way samba AD DC LDAP servers, handled 'Paged Results' control is combined with the 'ASQ' control. A malicious user in a samba AD could use this flaw to cause denial of service. This issue affects all samba versions before 4.10.15, before 4.11.8 and before 4.12.2.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U5KW3ZO35NVDO57JSBZHTQZOS3AIQ5QE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WG54NRMES2GTURZKZH6H4BGXCD3OMJDJ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Y7DVGCHG3XPIBQ5ETGMGW7MXNOO4HFH4/
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00002.html
- https://security.gentoo.org/glsa/202007-15
- https://www.samba.org/samba/security/CVE-2020-10700.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10700
