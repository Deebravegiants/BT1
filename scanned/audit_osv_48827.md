# [H] CVE-2018-14734

## Summary
Severity: High
Advisory: CVE-2018-14734
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-29
Source: https://osv.dev/vulnerability/CVE-2018-14734
Type: osv

## Details
drivers/infiniband/core/ucma.c in the Linux kernel through 4.17.11 allows ucma_leave_multicast to access a certain data structure after a cleanup step in ucma_process_join, which allows attackers to cause a denial of service (use-after-free).

## References
- https://access.redhat.com/errata/RHSA-2019:2043
- https://usn.ubuntu.com/3847-2/
- https://usn.ubuntu.com/3847-3/
- https://usn.ubuntu.com/3849-1/
- https://usn.ubuntu.com/3849-2/
- https://www.debian.org/security/2018/dsa-4308
- https://access.redhat.com/errata/RHSA-2019:2029
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3797-1/
- https://usn.ubuntu.com/3797-2/
- https://usn.ubuntu.com/3847-1/
- https://access.redhat.com/errata/RHSA-2019:0831
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=cb2595c1393b4a5211534e6f0a0fbad369e21ad8
- https://github.com/torvalds/linux/commit/cb2595c1393b4a5211534e6f0a0fbad369e21ad8
