# [M] CVE-2018-7740

## Summary
Severity: Medium
Advisory: CVE-2018-7740
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-07
Source: https://osv.dev/vulnerability/CVE-2018-7740
Type: osv

## Details
The resv_map_release function in mm/hugetlb.c in the Linux kernel through 4.15.7 allows local users to cause a denial of service (BUG) via a crafted application that makes mmap system calls and has a large pgoff argument to the remap_file_pages system call.

## References
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://usn.ubuntu.com/3910-1/
- https://usn.ubuntu.com/3910-2/
- http://www.securityfocus.com/bid/103316
- https://www.debian.org/security/2018/dsa-4187
- https://www.debian.org/security/2018/dsa-4188
- https://bugzilla.kernel.org/show_bug.cgi?id=199037
