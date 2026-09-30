# [H] CVE-2019-19448

## Summary
Severity: High
Advisory: CVE-2019-19448
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-08
Source: https://osv.dev/vulnerability/CVE-2019-19448
Type: osv

## Details
In the Linux kernel 5.0.21 and 5.3.11, mounting a crafted btrfs filesystem image, performing some operations, and then making a syncfs system call can lead to a use-after-free in try_merge_free_space in fs/btrfs/free-space-cache.c because the pointer to a left data structure can be the same as the pointer to a right data structure.

## References
- https://lists.debian.org/debian-lts-announce/2020/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00032.html
- https://lists.debian.org/debian-lts-announce/2020/10/msg00034.html
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4578-1/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19448
