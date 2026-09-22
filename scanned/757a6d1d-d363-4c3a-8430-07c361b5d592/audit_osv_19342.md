# [M] CVE-2021-20254

## Summary
Severity: Medium
Advisory: CVE-2021-20254
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-05-05
Source: https://osv.dev/vulnerability/CVE-2021-20254
Type: osv

## Details
A flaw was found in samba. The Samba smbd file server must map Windows group identities (SIDs) into unix group ids (gids). The code that performs this had a flaw that could allow it to read data beyond the end of the array in the case where a negative cache entry had been added to the mapping cache. This could cause the calling code to return those values into the process token that stores the group membership for a user. The highest threat from this vulnerability is to data confidentiality and integrity.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3EP2VJ73OVBPVSOSTVOMGIEQA3MWF6F7/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZAF6L2M6CNAJ2YYYGXPWETTW5YLCWTVT/
- https://lists.debian.org/debian-lts-announce/2021/05/msg00023.html
- https://security.gentoo.org/glsa/202105-22
- https://security.netapp.com/advisory/ntap-20210430-0001/
- https://www.samba.org/samba/security/CVE-2021-20254.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1949442
