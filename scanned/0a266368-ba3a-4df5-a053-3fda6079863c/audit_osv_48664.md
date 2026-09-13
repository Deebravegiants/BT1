# [M] CVE-2018-10881

## Summary
Severity: Medium
Advisory: CVE-2018-10881
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2018-10881
Type: osv

## Details
A flaw was found in the Linux kernel's ext4 filesystem. A local user can cause an out-of-bound access in ext4_get_group_info function, a denial of service, and a system crash by mounting and operating on a crafted ext4 filesystem image.

## References
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3754-1/
- http://www.securityfocus.com/bid/104901
- https://access.redhat.com/errata/RHSA-2018:3096
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://usn.ubuntu.com/3752-3/
- https://usn.ubuntu.com/3753-2/
- https://bugzilla.kernel.org/show_bug.cgi?id=200015
- http://patchwork.ozlabs.org/patch/929792/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10881
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6e8ab72a812396996035a37e5ca4b3b99b5d214b
