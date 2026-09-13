# [M] CVE-2018-18397

## Summary
Severity: Medium
Advisory: CVE-2018-18397
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-18397
Type: osv

## Details
The userfaultfd implementation in the Linux kernel before 4.19.7 mishandles access control for certain UFFDIO_ ioctl calls, as demonstrated by allowing local users to write data into holes in a tmpfs file (if the user has read-only access to that file, and that file contains holes), related to fs/userfaultfd.c and mm/userfaultfd.c.

## References
- https://access.redhat.com/errata/RHSA-2019:0324
- https://usn.ubuntu.com/3903-1/
- https://usn.ubuntu.com/3903-2/
- https://access.redhat.com/errata/RHBA-2019:0327
- https://access.redhat.com/errata/RHSA-2019:0163
- https://access.redhat.com/errata/RHSA-2019:0831
- https://usn.ubuntu.com/3901-1/
- https://usn.ubuntu.com/3901-2/
- https://access.redhat.com/errata/RHSA-2019:0202
- https://bugs.chromium.org/p/project-zero/issues/detail?id=1700
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.87
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.19.7
- https://github.com/torvalds/linux/commit/29ec90660d68bbdd69507c1c8b4e33aa299278b1
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=29ec90660d68bbdd69507c1c8b4e33aa299278b1
