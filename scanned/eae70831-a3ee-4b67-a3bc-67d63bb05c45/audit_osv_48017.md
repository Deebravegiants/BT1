# [M] CVE-2017-16994

## Summary
Severity: Medium
Advisory: CVE-2017-16994
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-27
Source: https://osv.dev/vulnerability/CVE-2017-16994
Type: osv

## Details
The walk_hugetlb_range function in mm/pagewalk.c in the Linux kernel before 4.14.2 mishandles holes in hugetlb ranges, which allows local users to obtain sensitive information from uninitialized kernel memory via crafted use of the mincore() system call.

## References
- https://usn.ubuntu.com/3619-1/
- https://usn.ubuntu.com/3632-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-2/
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-3/
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.2
- http://www.securityfocus.com/bid/101969
- https://access.redhat.com/errata/RHSA-2018:0502
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=373c4557d2aa362702c4c2d41288fb1e54990b7c
- https://github.com/torvalds/linux/commit/373c4557d2aa362702c4c2d41288fb1e54990b7c
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1431
- https://www.exploit-db.com/exploits/43178/
