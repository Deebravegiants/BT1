# [M] CVE-2018-14652

## Summary
Severity: Medium
Advisory: CVE-2018-14652
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-14652
Type: osv

## Details
The Gluster file system through versions 3.12 and 4.1.4 is vulnerable to a buffer overflow in the 'features/index' translator via the code handling the 'GF_XATTR_CLRLK_CMD' xattr in the 'pl_getxattr' function. A remote authenticated attacker could exploit this on a mounted volume to cause a denial of service.

## References
- https://security.gentoo.org/glsa/201904-06
- https://access.redhat.com/errata/RHSA-2018:3431
- https://access.redhat.com/errata/RHSA-2018:3432
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/11/msg00003.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14652
