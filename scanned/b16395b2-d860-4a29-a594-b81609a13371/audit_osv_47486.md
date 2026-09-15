# [H] CVE-2016-6786

## Summary
Severity: High
Advisory: CVE-2016-6786
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-6786
Type: osv

## Details
kernel/events/core.c in the performance subsystem in the Linux kernel before 4.0 mismanages locks during certain migrations, which allows local users to gain privileges via a crafted application, aka Android internal bug 30955111.

## References
- http://source.android.com/security/bulletin/2016-12-01.html
- http://www.debian.org/security/2017/dsa-3791
- http://www.securityfocus.com/bid/94679
- https://bugzilla.redhat.com/show_bug.cgi?id=1403842
- https://github.com/torvalds/linux/commit/f63a8daa5812afef4f06c962351687e1ff9ccb2b
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=f63a8daa5812afef4f06c962351687e1ff9ccb2b
