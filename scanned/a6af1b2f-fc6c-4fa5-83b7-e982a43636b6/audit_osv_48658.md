# [M] CVE-2018-10876

## Summary
Severity: Medium
Advisory: CVE-2018-10876
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-26
Source: https://osv.dev/vulnerability/CVE-2018-10876
Type: osv

## Details
A flaw was found in Linux kernel in the ext4 filesystem code. A use-after-free is possible in ext4_ext_remove_space() function when mounting and operating a crafted ext4 image.

## References
- http://www.securityfocus.com/bid/104904
- http://www.securityfocus.com/bid/106503
- https://access.redhat.com/errata/RHSA-2019:0525
- https://usn.ubuntu.com/3753-1/
- https://usn.ubuntu.com/3753-2/
- https://usn.ubuntu.com/3871-1/
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-4/
- https://usn.ubuntu.com/3871-5/
- https://bugzilla.kernel.org/show_bug.cgi?id=199403
- http://patchwork.ozlabs.org/patch/929239/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10876
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8844618d8aa7a9973e7b527d038a2a589665002c
