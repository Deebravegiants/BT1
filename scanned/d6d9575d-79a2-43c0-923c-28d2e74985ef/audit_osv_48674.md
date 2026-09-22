# [M] CVE-2018-1093

## Summary
Severity: Medium
Advisory: CVE-2018-1093
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-04-02
Source: https://osv.dev/vulnerability/CVE-2018-1093
Type: osv

## Details
The ext4_valid_block_bitmap function in fs/ext4/balloc.c in the Linux kernel through 4.15.15 allows attackers to cause a denial of service (out-of-bounds read and system crash) via a crafted ext4 image because balloc.c and ialloc.c do not validate bitmap block numbers.

## References
- https://lists.debian.org/debian-lts-announce/2018/06/msg00000.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00015.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00016.html
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3754-1/
- https://usn.ubuntu.com/3676-1/
- https://usn.ubuntu.com/3676-2/
- https://usn.ubuntu.com/3752-3/
- https://www.debian.org/security/2018/dsa-4188
- https://bugzilla.kernel.org/show_bug.cgi?id=199181
- https://bugzilla.redhat.com/show_bug.cgi?id=1560782
- https://git.kernel.org/pub/scm/linux/kernel/git/tytso/ext4.git/commit/?id=7dac4a1726a9c64a517d595c40e95e2d0d135f6f
- http://openwall.com/lists/oss-security/2018/03/29/1
