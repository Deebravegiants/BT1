# [H] CVE-2017-16939

## Summary
Severity: High
Advisory: CVE-2017-16939
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-24
Source: https://osv.dev/vulnerability/CVE-2017-16939
Type: osv

## Details
The XFRM dump policy implementation in net/xfrm/xfrm_user.c in the Linux kernel before 4.13.11 allows local users to gain privileges or cause a denial of service (use-after-free) via a crafted SO_RCVBUF setsockopt system call in conjunction with XFRM_MSG_GETPOLICY Netlink messages.

## References
- http://lists.opensuse.org/opensuse-security-announce/2018-01/msg00007.html
- http://www.securityfocus.com/bid/101954
- https://access.redhat.com/errata/RHSA-2018:1355
- https://access.redhat.com/errata/RHSA-2019:1170
- https://access.redhat.com/errata/RHSA-2019:1190
- http://seclists.org/fulldisclosure/2017/Nov/40
- https://access.redhat.com/errata/RHSA-2018:1318
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://www.debian.org/security/2018/dsa-4082
- https://bugzilla.suse.com/show_bug.cgi?id=1069702
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1137b5e2529a8f5ca8ee709288ecba3e68044df2
- https://blogs.securiteam.com/index.php/archives/3535
- https://github.com/torvalds/linux/commit/1137b5e2529a8f5ca8ee709288ecba3e68044df2
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.11
