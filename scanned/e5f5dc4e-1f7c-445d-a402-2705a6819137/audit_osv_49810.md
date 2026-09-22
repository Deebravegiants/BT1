# [M] CVE-2019-19318

## Summary
Severity: Medium
Advisory: CVE-2019-19318
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-28
Source: https://osv.dev/vulnerability/CVE-2019-19318
Type: osv

## Details
In the Linux kernel 5.3.11, mounting a crafted btrfs image twice can cause an rwsem_down_write_slowpath use-after-free because (in rwsem_can_spin_on_owner in kernel/locking/rwsem.c) rwsem_owner_flags returns an already freed pointer,

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20200103-0001/
- https://usn.ubuntu.com/4414-1/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19318
