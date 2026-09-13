# [C] CVE-2016-7117

## Summary
Severity: Critical
Advisory: CVE-2016-7117
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2016-7117
Type: osv

## Details
Use-after-free vulnerability in the __sys_recvmmsg function in net/socket.c in the Linux kernel before 4.5.2 allows remote attackers to execute arbitrary code via vectors involving a recvmmsg system call that is mishandled during error processing.

## References
- http://rhn.redhat.com/errata/RHSA-2017-0065.html
- http://rhn.redhat.com/errata/RHSA-2017-0091.html
- http://rhn.redhat.com/errata/RHSA-2017-0196.html
- http://rhn.redhat.com/errata/RHSA-2017-0217.html
- http://www.securityfocus.com/bid/93304
- http://rhn.redhat.com/errata/RHSA-2016-2962.html
- http://rhn.redhat.com/errata/RHSA-2017-0216.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.5.2
- http://rhn.redhat.com/errata/RHSA-2017-0036.html
- http://rhn.redhat.com/errata/RHSA-2017-0113.html
- http://rhn.redhat.com/errata/RHSA-2017-0215.html
- http://rhn.redhat.com/errata/RHSA-2017-0270.html
- http://source.android.com/security/bulletin/2016-10-01.html
- http://rhn.redhat.com/errata/RHSA-2017-0031.html
- http://rhn.redhat.com/errata/RHSA-2017-0086.html
- https://people.canonical.com/~ubuntu-security/cve/2016/CVE-2016-7117.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1382268
- https://security-tracker.debian.org/tracker/CVE-2016-7117
- https://bugzilla.novell.com/show_bug.cgi?id=1003077
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=34b88a68f26a75e4fded796f1a49c40f82234b7d
