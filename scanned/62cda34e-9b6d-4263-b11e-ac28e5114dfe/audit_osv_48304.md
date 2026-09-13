# [H] CVE-2017-6001

## Summary
Severity: High
Advisory: CVE-2017-6001
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-18
Source: https://osv.dev/vulnerability/CVE-2017-6001
Type: osv

## Details
Race condition in kernel/events/core.c in the Linux kernel before 4.9.7 allows local users to gain privileges via a crafted application that makes concurrent perf_event_open system calls for moving a software group into a hardware context.  NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-6786.

## References
- http://www.debian.org/security/2017/dsa-3791
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.9.7
- http://www.securityfocus.com/bid/96264
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2669
- https://access.redhat.com/errata/RHSA-2018:1854
- https://access.redhat.com/errata/RHSA-2017:2077
- https://source.android.com/security/bulletin/pixel/2017-11-01
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=321027c1fe77f892f4ea07846aeae08cefbbb290
- http://www.openwall.com/lists/oss-security/2017/02/16/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1422825
- https://github.com/torvalds/linux/commit/321027c1fe77f892f4ea07846aeae08cefbbb290
