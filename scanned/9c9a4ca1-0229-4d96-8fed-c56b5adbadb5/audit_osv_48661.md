# [H] CVE-2018-10879

## Summary
Severity: High
Advisory: CVE-2018-10879
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2018-10879
Type: osv

## Details
A flaw was found in the Linux kernel's ext4 filesystem. A local user can cause a use-after-free in ext4_xattr_set_entry function and a denial of service or unspecified other impact may occur by renaming a file in a crafted ext4 filesystem image.

## References
- https://access.redhat.com/errata/RHSA-2018:3083
- https://access.redhat.com/errata/RHSA-2018:3096
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3871-1/
- http://www.securityfocus.com/bid/104902
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-5/
- https://usn.ubuntu.com/3753-2/
- https://usn.ubuntu.com/3871-4/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://bugzilla.kernel.org/show_bug.cgi?id=200001
- http://patchwork.ozlabs.org/patch/928666/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=513f86d73855ce556ea9522b6bfd79f87356dc3a
- http://patchwork.ozlabs.org/patch/928667/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10879
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=5369a762c882c0b6e9599e4ebbb3a9ba9eee7e2d
