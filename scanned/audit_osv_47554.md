# [M] CVE-2016-7917

## Summary
Severity: Medium
Advisory: CVE-2016-7917
CVSS: 5.0 (CVSS:3.0/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-7917
Type: osv

## Details
The nfnetlink_rcv_batch function in net/netfilter/nfnetlink.c in the Linux kernel before 4.5 does not check whether a batch message's length field is large enough, which allows local users to obtain sensitive information from kernel memory or cause a denial of service (infinite loop or out-of-bounds read) by leveraging the CAP_NET_ADMIN capability.

## References
- http://source.android.com/security/bulletin/2016-11-01.html
- http://www.securityfocus.com/bid/94147
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=c58d6c93680f28ac58984af61d0a7ebf4319c241
- https://github.com/torvalds/linux/commit/c58d6c93680f28ac58984af61d0a7ebf4319c241
