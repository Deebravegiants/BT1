# [H] CVE-2016-7911

## Summary
Severity: High
Advisory: CVE-2016-7911
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7911
Type: osv

## Details
Race condition in the get_task_ioprio function in block/ioprio.c in the Linux kernel before 4.6.6 allows local users to gain privileges or cause a denial of service (use-after-free) via a crafted ioprio_get system call.

## References
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.6
- http://www.securityfocus.com/bid/94135
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=8ba8682107ee2ca3347354e018865d8e1967c5f4
- https://github.com/torvalds/linux/commit/8ba8682107ee2ca3347354e018865d8e1967c5f4
