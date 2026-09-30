# [M] CVE-2014-0203

## Summary
Severity: Medium
Advisory: CVE-2014-0203
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2014-06-23
Source: https://osv.dev/vulnerability/CVE-2014-0203
Type: osv

## Details
The __do_follow_link function in fs/namei.c in the Linux kernel before 2.6.33 does not properly handle the last pathname component during use of certain filesystems, which allows local users to cause a denial of service (incorrect free operations and system crash) via an open system call.

## References
- http://linux.oracle.com/errata/ELSA-2014-0771.html
- http://linux.oracle.com/errata/ELSA-2014-3043.html
- http://secunia.com/advisories/59262
- http://secunia.com/advisories/59309
- http://secunia.com/advisories/59406
- http://secunia.com/advisories/59560
- http://www.securityfocus.com/bid/68125
- https://bugzilla.redhat.com/show_bug.cgi?id=1094363
- https://github.com/torvalds/linux/commit/86acdca1b63e6890540fa19495cfc708beff3d8b
- https://bugzilla.redhat.com/show_bug.cgi?id=1094363
- https://bugzilla.redhat.com/show_bug.cgi?id=1094363
- https://github.com/torvalds/linux/commit/86acdca1b63e6890540fa19495cfc708beff3d8b
- https://bugzilla.redhat.com/show_bug.cgi?id=1094363
- http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git%3Ba=commit%3Bh=86acdca1b63e6890540fa19495cfc708beff3d8b
- http://mirror.linux.org.au/linux/kernel/v2.6/ChangeLog-2.6.33
