# [M] CVE-2016-9191

## Summary
Severity: Medium
Advisory: CVE-2016-9191
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-9191
Type: osv

## Details
The cgroup offline implementation in the Linux kernel through 4.8.11 mishandles certain drain operations, which allows local users to cause a denial of service (system hang) by leveraging access to a container environment for executing a crafted application, as demonstrated by trinity.

## References
- https://support.hpe.com/hpsc/doc/public/display?docLocale=en_US&docId=emr_na-hpesbhf03802en_us
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=93362fa47fe98b62e4a34ab408c4a418432e7939
- http://www.debian.org/security/2017/dsa-3791
- http://www.openwall.com/lists/oss-security/2016/11/05/4
- http://www.securityfocus.com/bid/94129
- https://bugzilla.redhat.com/show_bug.cgi?id=1392439
- https://github.com/torvalds/linux/commit/93362fa47fe98b62e4a34ab408c4a418432e7939
