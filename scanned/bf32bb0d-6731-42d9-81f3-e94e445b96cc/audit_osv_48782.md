# [M] CVE-2018-13098

## Summary
Severity: Medium
Advisory: CVE-2018-13098
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-07-03
Source: https://osv.dev/vulnerability/CVE-2018-13098
Type: osv

## Details
An issue was discovered in fs/f2fs/inode.c in the Linux kernel through 4.17.3. A denial of service (slab out-of-bounds read and BUG) can occur for a modified f2fs filesystem image in which FI_EXTRA_ATTR is set in an inode.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-10/msg00033.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=76d56d4ab4f2a9e4f085c7d77172194ddaccf7d2
- https://usn.ubuntu.com/4094-1/
- https://usn.ubuntu.com/4118-1/
- https://bugzilla.kernel.org/show_bug.cgi?id=200173
