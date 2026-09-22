# [H] CVE-2019-19770

## Summary
Severity: High
Advisory: CVE-2019-19770
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2019-12-12
Source: https://osv.dev/vulnerability/CVE-2019-19770
Type: osv

## Details
In the Linux kernel 4.19.83, there is a use-after-free (read) in the debugfs_remove function in fs/debugfs/inode.c (which is used to remove a file or directory in debugfs that was previously created with a call to another debugfs function such as debugfs_create_file). NOTE: Linux kernel developers dispute this issue as not being an issue with debugfs, instead this is an issue with misuse of debugfs within blktrace

## References
- https://lore.kernel.org/linux-block/20200402000002.7442-1-mcgrof%40kernel.org/
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://bugzilla.kernel.org/show_bug.cgi?id=205713
