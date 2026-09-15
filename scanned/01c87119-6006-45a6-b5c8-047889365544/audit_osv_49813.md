# [H] CVE-2019-19377

## Summary
Severity: High
Advisory: CVE-2019-19377
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-11-29
Source: https://osv.dev/vulnerability/CVE-2019-19377
Type: osv

## Details
In the Linux kernel 5.0.21, mounting a crafted btrfs filesystem image, performing some operations, and unmounting can lead to a use-after-free in btrfs_queue_work in fs/btrfs/async-thread.c.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4367-1/
- https://usn.ubuntu.com/4369-1/
- https://usn.ubuntu.com/4414-1/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19377
