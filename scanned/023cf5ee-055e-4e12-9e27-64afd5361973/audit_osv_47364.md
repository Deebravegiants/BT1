# [H] CVE-2016-3841

## Summary
Severity: High
Advisory: CVE-2016-3841
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-08-06
Source: https://osv.dev/vulnerability/CVE-2016-3841
Type: osv

## Details
The IPv6 stack in the Linux kernel before 4.3.3 mishandles options data, which allows local users to gain privileges or cause a denial of service (use-after-free and system crash) via a crafted sendmsg system call.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2695.html
- http://source.android.com/security/bulletin/2016-08-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.3.3
- http://rhn.redhat.com/errata/RHSA-2016-0855.html
- http://www.securityfocus.com/bid/92227
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- https://github.com/torvalds/linux/commit/45f6fad84cc305103b28d73482b344d7f5b76f39
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=45f6fad84cc305103b28d73482b344d7f5b76f39
