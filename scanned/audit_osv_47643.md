# [H] CVE-2016-9806

## Summary
Severity: High
Advisory: CVE-2016-9806
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-28
Source: https://osv.dev/vulnerability/CVE-2016-9806
Type: osv

## Details
Race condition in the netlink_dump function in net/netlink/af_netlink.c in the Linux kernel before 4.6.3 allows local users to cause a denial of service (double free) or possibly have unspecified other impact via a crafted application that makes sendmsg system calls, leading to a free operation associated with a new dump that started earlier than anticipated.

## References
- http://lists.openwall.net/netdev/2016/05/15/69
- http://www.securityfocus.com/bid/94653
- http://www.securitytracker.com/id/1037968
- https://access.redhat.com/errata/RHSA-2017:1842
- https://access.redhat.com/errata/RHSA-2017:2077
- https://source.android.com/security/bulletin/2017-03-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.6.3
- https://access.redhat.com/errata/RHSA-2017:2669
- https://github.com/torvalds/linux/commit/92964c79b357efd980812c4de5c1fd2ec8bb5520
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=92964c79b357efd980812c4de5c1fd2ec8bb5520
- http://www.openwall.com/lists/oss-security/2016/12/03/4
- https://bugzilla.redhat.com/show_bug.cgi?id=1401502
