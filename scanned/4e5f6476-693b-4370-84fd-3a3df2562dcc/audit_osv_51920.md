# [H] CVE-2021-45469

## Summary
Severity: High
Advisory: CVE-2021-45469
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-45469
Type: osv

## Details
In __f2fs_setxattr in fs/f2fs/xattr.c in the Linux kernel through 5.15.11, there is an out-of-bounds memory access when an inode has an invalid last xattr entry.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/AK2C4A43BZSWATZWFUHHHUQF3HPIALNP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QG7XV2WXKMSMKIQKIBG5LW3Y3GXEWG5Q/
- https://security.netapp.com/advisory/ntap-20220114-0003/
- http://www.openwall.com/lists/oss-security/2021/12/25/1
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://www.debian.org/security/2022/dsa-5050
- https://www.debian.org/security/2022/dsa-5096
- https://git.kernel.org/pub/scm/linux/kernel/git/chao/linux.git/commit/?h=dev&id=5598b24efaf4892741c798b425d543e4bed357a1
- https://bugzilla.kernel.org/show_bug.cgi?id=215235
