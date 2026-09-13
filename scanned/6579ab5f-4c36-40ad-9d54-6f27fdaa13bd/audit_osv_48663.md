# [M] CVE-2018-10880

## Summary
Severity: Medium
Advisory: CVE-2018-10880
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-25
Source: https://osv.dev/vulnerability/CVE-2018-10880
Type: osv

## Details
Linux kernel is vulnerable to a stack-out-of-bounds write in the ext4 filesystem code when mounting and writing to a crafted ext4 image in ext4_update_inline_data(). An attacker could use this to cause a system crash and a denial of service.

## References
- http://www.securityfocus.com/bid/104907
- http://www.securityfocus.com/bid/106503
- https://lists.debian.org/debian-lts-announce/2018/07/msg00020.html
- https://usn.ubuntu.com/3821-2/
- https://usn.ubuntu.com/3871-1/
- https://usn.ubuntu.com/3871-4/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://usn.ubuntu.com/3821-1/
- https://usn.ubuntu.com/3871-3/
- https://usn.ubuntu.com/3871-5/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=8cdb5240ec5928b20490a2bb34cb87e9a5f40226
- https://bugzilla.kernel.org/show_bug.cgi?id=200005
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-10880
- http://patchwork.ozlabs.org/patch/930639/
