# [H] CVE-2016-8632

## Summary
Severity: High
Advisory: CVE-2016-8632
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-11-28
Source: https://osv.dev/vulnerability/CVE-2016-8632
Type: osv

## Details
The tipc_msg_build function in net/tipc/msg.c in the Linux kernel through 4.8.11 does not validate the relationship between the minimum fragment length and the maximum packet size, which allows local users to gain privileges or cause a denial of service (heap-based buffer overflow) by leveraging the CAP_NET_ADMIN capability.

## References
- https://www.mail-archive.com/netdev%40vger.kernel.org/msg133205.html
- http://www.openwall.com/lists/oss-security/2016/11/08/5
- http://www.securityfocus.com/bid/94211
- https://bugzilla.redhat.com/show_bug.cgi?id=1390832
