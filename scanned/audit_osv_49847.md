# [M] CVE-2019-19813

## Summary
Severity: Medium
Advisory: CVE-2019-19813
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-17
Source: https://osv.dev/vulnerability/CVE-2019-19813
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted btrfs filesystem image, performing some operations, and then making a syncfs system call can lead to a use-after-free in __mutex_lock in kernel/locking/mutex.c. This is related to mutex_can_spin_on_owner in kernel/locking/mutex.c, __btrfs_qgroup_free_meta in fs/btrfs/qgroup.c, and btrfs_insert_delayed_items in fs/btrfs/delayed-inode.c.

## References
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4414-1/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19813
