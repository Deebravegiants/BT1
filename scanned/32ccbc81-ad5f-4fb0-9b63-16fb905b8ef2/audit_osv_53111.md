# [H] CVE-2022-2978

## Summary
Severity: High
Advisory: CVE-2022-2978
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2022-2978
Type: osv

## Details
A flaw use after free in the Linux kernel NILFS file system was found in the way user triggers function security_inode_alloc to fail with following call to function nilfs_mdt_destroy. A local user could use this flaw to crash the system or potentially escalate their privileges on the system.

## References
- https://lore.kernel.org/linux-fsdevel/20220816040859.659129-1-dzm91%40hust.edu.cn/T/#u
- https://lists.debian.org/debian-lts-announce/2022/12/msg00034.html
