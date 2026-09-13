# [H] CVE-2014-7825

## Summary
Severity: High
Advisory: CVE-2014-7825
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-11-10
Source: https://osv.dev/vulnerability/CVE-2014-7825
Type: osv

## Details
kernel/trace/trace_syscalls.c in the Linux kernel through 3.17.2 does not properly handle private syscall numbers during use of the perf subsystem, which allows local users to cause a denial of service (out-of-bounds read and OOPS) or bypass the ASLR protection mechanism via a crafted application.

## References
- http://rhn.redhat.com/errata/RHSA-2014-1943.html
- http://rhn.redhat.com/errata/RHSA-2015-0290.html
- http://rhn.redhat.com/errata/RHSA-2015-0864.html
- http://www.openwall.com/lists/oss-security/2014/11/06/11
- http://www.securityfocus.com/bid/70972
- https://bugzilla.redhat.com/show_bug.cgi?id=1161565
- https://exchange.xforce.ibmcloud.com/vulnerabilities/98557
- https://github.com/torvalds/linux/commit/086ba77a6db00ed858ff07451bedee197df868c9
- http://www.openwall.com/lists/oss-security/2014/11/06/11
- https://github.com/torvalds/linux/commit/086ba77a6db00ed858ff07451bedee197df868c9
- http://www.openwall.com/lists/oss-security/2014/11/06/11
- https://bugzilla.redhat.com/show_bug.cgi?id=1161565
- https://github.com/torvalds/linux/commit/086ba77a6db00ed858ff07451bedee197df868c9
- https://bugzilla.redhat.com/show_bug.cgi?id=1161565
- http://git.kernel.org/?p=linux/kernel/git/torvalds/linux-2.6.git%3Ba=commit%3Bh=086ba77a6db00ed858ff07451bedee197df868c9
