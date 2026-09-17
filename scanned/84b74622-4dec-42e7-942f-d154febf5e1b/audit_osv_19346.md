# [M] CVE-2021-20266

## Summary
Severity: Medium
Advisory: CVE-2021-20266
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-04-30
Source: https://osv.dev/vulnerability/CVE-2021-20266
Type: osv

## Details
A flaw was found in RPM's hdrblobInit() in lib/header.c. This flaw allows an attacker who can modify the rpmdb to cause an out-of-bounds read. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TMGXO3W6DHPO62GJ4VVF5DEUX5DRUR5K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VHRPNBCRPDJHHQE3MBPSZK4H7X2IM7AC/
- https://security.gentoo.org/glsa/202107-43
- https://bugzilla.redhat.com/show_bug.cgi?id=1927741
