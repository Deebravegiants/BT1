# [M] CVE-2016-8633

## Summary
Severity: Medium
Advisory: CVE-2016-8633
CVSS: 6.8 (CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-8633
Type: osv

## Details
drivers/firewire/net.c in the Linux kernel before 4.8.7, in certain unusual hardware configurations, allows remote attackers to execute arbitrary code via crafted fragmented packets.

## References
- http://www.securityfocus.com/bid/94149
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.8.7
- http://www.openwall.com/lists/oss-security/2016/11/06/1
- https://access.redhat.com/errata/RHSA-2018:0676
- https://access.redhat.com/errata/RHSA-2019:1170
- https://access.redhat.com/errata/RHSA-2019:1190
- https://access.redhat.com/errata/RHSA-2018:1062
- https://eyalitkin.wordpress.com/2016/11/06/cve-publication-cve-2016-8633/
- https://bugzilla.redhat.com/show_bug.cgi?id=1391490
- https://github.com/torvalds/linux/commit/667121ace9dbafb368618dbabcf07901c962ddac
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=667121ace9dbafb368618dbabcf07901c962ddac
