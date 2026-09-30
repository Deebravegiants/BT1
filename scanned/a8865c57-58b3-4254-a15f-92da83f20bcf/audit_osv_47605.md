# [H] CVE-2016-9120

## Summary
Severity: High
Advisory: CVE-2016-9120
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-12-08
Source: https://osv.dev/vulnerability/CVE-2016-9120
Type: osv

## Details
Race condition in the ion_ioctl function in drivers/staging/android/ion/ion.c in the Linux kernel before 4.6 allows local users to gain privileges or cause a denial of service (use-after-free) by calling ION_IOC_FREE on two CPUs at the same time.

## References
- http://www.securityfocus.com/bid/94669
- http://source.android.com/security/bulletin/2016-12-01.html
- https://github.com/torvalds/linux/commit/9590232bb4f4cc824f3425a6e1349afbe6d6d2b7
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=9590232bb4f4cc824f3425a6e1349afbe6d6d2b7
