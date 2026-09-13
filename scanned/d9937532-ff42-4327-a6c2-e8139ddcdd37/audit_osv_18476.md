# [H] CVE-2020-27840

## Summary
Severity: High
Advisory: CVE-2020-27840
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-05-12
Source: https://osv.dev/vulnerability/CVE-2020-27840
Type: osv

## Details
A flaw was found in samba. Spaces used in a string around a domain name (DN), while supposed to be ignored, can cause invalid DN strings with spaces to instead write a zero-byte into out-of-bounds memory, resulting in a crash. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VLZ74IF2N75VQSIHBL4B3P5WKWQCXSRY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X5J3B6PN5XMXF3OHYBNHDKZ3XFSUGY4L/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZXP3ONIY6MB4C5LDZV4YL5KJCES3UX24/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00036.html
- https://security.gentoo.org/glsa/202105-22
- https://security.netapp.com/advisory/ntap-20210326-0007/
- https://www.debian.org/security/2021/dsa-4884
- https://www.samba.org/samba/security/CVE-2020-27840.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1941400
