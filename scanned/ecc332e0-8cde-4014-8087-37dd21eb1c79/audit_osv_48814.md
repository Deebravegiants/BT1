# [M] CVE-2018-14617

## Summary
Severity: Medium
Advisory: CVE-2018-14617
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-27
Source: https://osv.dev/vulnerability/CVE-2018-14617
Type: osv

## Details
An issue was discovered in the Linux kernel through 4.17.10. There is a NULL pointer dereference and panic in hfsplus_lookup() in fs/hfsplus/dir.c when opening a file (that is purportedly a hard link) in an hfs+ filesystem that has malformed catalog data, and is mounted read-only without a metadata directory.

## References
- https://usn.ubuntu.com/4118-1/
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/3821-1/
- https://usn.ubuntu.com/3821-2/
- http://www.securityfocus.com/bid/104917
- https://www.debian.org/security/2018/dsa-4308
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://bugzilla.kernel.org/show_bug.cgi?id=200297
- https://www.spinics.net/lists/linux-fsdevel/msg130021.html
