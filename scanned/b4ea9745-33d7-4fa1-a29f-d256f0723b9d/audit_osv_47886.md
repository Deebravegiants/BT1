# [M] CVE-2017-14340

## Summary
Severity: Medium
Advisory: CVE-2017-14340
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-09-15
Source: https://osv.dev/vulnerability/CVE-2017-14340
Type: osv

## Details
The XFS_IS_REALTIME_INODE macro in fs/xfs/xfs_linux.h in the Linux kernel before 4.13.2 does not verify that a filesystem has a realtime device, which allows local users to cause a denial of service (NULL pointer dereference and OOPS) via vectors related to setting an RHINHERIT flag on a directory.

## References
- http://www.debian.org/security/2017/dsa-3981
- http://www.securityfocus.com/bid/100851
- https://access.redhat.com/errata/RHSA-2017:2918
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.2
- https://bugzilla.redhat.com/show_bug.cgi?id=1491344
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b31ff3cdf540110da4572e3e29bd172087af65cc
- http://seclists.org/oss-sec/2017/q3/436
- https://github.com/torvalds/linux/commit/b31ff3cdf540110da4572e3e29bd172087af65cc
