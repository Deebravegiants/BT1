# [H] CVE-2018-18281

## Summary
Severity: High
Advisory: CVE-2018-18281
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-30
Source: https://osv.dev/vulnerability/CVE-2018-18281
Type: osv

## Details
Since Linux kernel version 3.2, the mremap() syscall performs TLB flushes after dropping pagetable locks. If a syscall such as ftruncate() removes entries from the pagetables of a task that is in the middle of mremap(), a stale TLB entry can remain for a short time that permits access to a physical page after it has been released back to the page allocator and reused. This is fixed in the following kernel versions: 4.9.135, 4.14.78, 4.18.16, 4.19.

## References
- http://www.securityfocus.com/bid/105761
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2020:0036
- https://lists.debian.org/debian-lts-announce/2019/03/msg00034.html
- https://usn.ubuntu.com/3835-1/
- https://usn.ubuntu.com/3871-4/
- https://usn.ubuntu.com/3880-2/
- https://access.redhat.com/errata/RHSA-2019:2043
- https://access.redhat.com/errata/RHSA-2020:0100
- https://access.redhat.com/errata/RHSA-2020:0103
- https://lists.debian.org/debian-lts-announce/2019/03/msg00017.html
- https://usn.ubuntu.com/3871-1/
- http://www.securityfocus.com/bid/106503
- https://access.redhat.com/errata/RHSA-2019:0831
- https://lists.debian.org/debian-lts-announce/2019/04/msg00004.html
- https://usn.ubuntu.com/3832-1/
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3880-1/
- https://access.redhat.com/errata/RHSA-2020:0179
- https://usn.ubuntu.com/3871-3/
