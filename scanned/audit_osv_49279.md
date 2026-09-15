# [H] CVE-2018-8781

## Summary
Severity: High
Advisory: CVE-2018-8781
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-23
Source: https://osv.dev/vulnerability/CVE-2018-8781
Type: osv

## Details
The udl_fb_mmap function in drivers/gpu/drm/udl/udl_fb.c at the Linux kernel version 3.4 and up to and including 4.15 has an integer-overflow vulnerability allowing local users with access to the udldrmfb driver to obtain full read and write permissions on kernel physical pages, resulting in a code execution in kernel space.

## References
- https://lists.debian.org/debian-lts-announce/2018/05/msg00000.html
- https://research.checkpoint.com/mmap-vulnerabilities-linux-kernel/
- https://usn.ubuntu.com/3677-2/
- https://www.debian.org/security/2018/dsa-4188
- https://access.redhat.com/errata/RHSA-2018:3096
- https://usn.ubuntu.com/3654-1/
- https://usn.ubuntu.com/3654-2/
- https://usn.ubuntu.com/3656-1/
- https://usn.ubuntu.com/3674-1/
- https://access.redhat.com/errata/RHSA-2018:2948
- https://access.redhat.com/errata/RHSA-2018:3083
- https://usn.ubuntu.com/3674-2/
- https://usn.ubuntu.com/3677-1/
- https://www.debian.org/security/2018/dsa-4187
- https://patchwork.freedesktop.org/patch/211845/
