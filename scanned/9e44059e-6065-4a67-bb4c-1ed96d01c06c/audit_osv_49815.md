# [H] CVE-2019-19447

## Summary
Severity: High
Advisory: CVE-2019-19447
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-08
Source: https://osv.dev/vulnerability/CVE-2019-19447
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted ext4 filesystem image, performing some operations, and unmounting can lead to a use-after-free in ext4_put_super in fs/ext4/super.c, related to dump_orphan_list in fs/ext4/super.c.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00011.html
- https://lists.debian.org/debian-lts-announce/2020/06/msg00013.html
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19447
