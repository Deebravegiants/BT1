# [M] CVE-2021-4155

## Summary
Severity: Medium
Advisory: CVE-2021-4155
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-4155
Type: osv

## Details
A data leak flaw was found in the way XFS_IOC_ALLOCSP IOCTL in the XFS filesystem allowed for size increase of files with unaligned size. A local attacker could use this flaw to leak data on the XFS filesystem otherwise not accessible to them.

## References
- https://access.redhat.com/security/cve/CVE-2021-4155
- https://security-tracker.debian.org/tracker/CVE-2021-4155
- https://bugzilla.redhat.com/show_bug.cgi?id=2034813
- https://www.openwall.com/lists/oss-security/2022/01/10/1
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=983d8e60f50806f90534cc5373d0ce867e5aaf79
