# [M] CVE-2019-19037

## Summary
Severity: Medium
Advisory: CVE-2019-19037
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-19037
Type: osv

## Details
ext4_empty_dir in fs/ext4/namei.c in the Linux kernel through 5.3.12 allows a NULL pointer dereference because ext4_read_dirblock(inode,0,DIRENT_HTREE) can be zero.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19037
