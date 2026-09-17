# [M] CVE-2020-14311

## Summary
Severity: Medium
Advisory: CVE-2020-14311
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2020-07-31
Source: https://osv.dev/vulnerability/CVE-2020-14311
Type: osv

## Details
There is an issue with grub2 before version 2.06 while handling symlink on ext filesystems. A filesystem containing a symbolic link with an inode size of UINT32_MAX causes an arithmetic overflow leading to a zero-sized memory allocation with subsequent heap-based buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2021/09/21/1
- https://security.gentoo.org/glsa/202104-05
- https://usn.ubuntu.com/4432-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2020-08/msg00017.html
- http://www.openwall.com/lists/oss-security/2021/09/17/2
- http://www.openwall.com/lists/oss-security/2021/09/17/4
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-14311
