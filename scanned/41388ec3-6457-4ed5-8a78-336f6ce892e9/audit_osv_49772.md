# [M] CVE-2019-19039

## Summary
Severity: Medium
Advisory: CVE-2019-19039
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2019-11-21
Source: https://osv.dev/vulnerability/CVE-2019-19039
Type: osv

## Details
__btrfs_free_extent in fs/btrfs/extent-tree.c in the Linux kernel through 5.3.12 calls btrfs_print_leaf in a certain ENOENT case, which allows local users to obtain potentially sensitive information about register values via the dmesg program. NOTE: The BTRFS development team disputes this issues as not being a vulnerability because “1) The kernel provide facilities to restrict access to dmesg - dmesg_restrict=1 sysctl option. So it's really up to the system administrator to judge whether dmesg access shall be disallowed or not. 2) WARN/WARN_ON are widely used macros in the linux kernel. If this CVE is considered valid this would mean there are literally thousands CVE lurking in the kernel - something which clearly is not the case.

## References
- https://lists.debian.org/debian-lts-announce/2020/12/msg00015.html
- https://usn.ubuntu.com/4414-1/
- https://github.com/bobfuzzer/CVE/tree/master/CVE-2019-19039
