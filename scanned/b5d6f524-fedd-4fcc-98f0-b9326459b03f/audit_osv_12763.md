# [M] CVE-2018-14659

## Summary
Severity: Medium
Advisory: CVE-2018-14659
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-10-31
Source: https://osv.dev/vulnerability/CVE-2018-14659
Type: osv

## Details
The Gluster file system through versions 4.1.4 and 3.1.2 is vulnerable to a denial of service attack via use of the 'GF_XATTR_IOSTATS_DUMP_KEY' xattr. A remote, authenticated attacker could exploit this by mounting a Gluster volume and repeatedly calling 'setxattr(2)' to trigger a state dump and create an arbitrary number of files in the server's runtime directory.

## References
- https://access.redhat.com/errata/RHSA-2018:3431
- https://access.redhat.com/errata/RHSA-2018:3432
- https://access.redhat.com/errata/RHSA-2018:3470
- https://lists.debian.org/debian-lts-announce/2018/11/msg00003.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00000.html
- https://security.gentoo.org/glsa/201904-06
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-14659
