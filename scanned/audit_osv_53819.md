# [H] CVE-2023-26605

## Summary
Severity: High
Advisory: CVE-2023-26605
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-26
Source: https://osv.dev/vulnerability/CVE-2023-26605
Type: osv

## Details
In the Linux kernel 6.0.8, there is a use-after-free in inode_cgwb_move_to_attached in fs/fs-writeback.c, related to __list_del_entry_valid.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4e3c51f4e805291b057d12f5dda5aeb50a538dc4
- https://security.netapp.com/advisory/ntap-20230316-0010/
- https://lkml.org/lkml/2023/2/22/3
