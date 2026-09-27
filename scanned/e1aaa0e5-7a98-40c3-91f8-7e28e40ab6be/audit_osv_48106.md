# [H] CVE-2017-18218

## Summary
Severity: High
Advisory: CVE-2017-18218
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/CVE-2017-18218
Type: osv

## Details
In drivers/net/ethernet/hisilicon/hns/hns_enet.c in the Linux kernel before 4.13, local users can cause a denial of service (use-after-free and BUG) or possibly have unspecified other impact by leveraging differences in skb handling between hns_nic_net_xmit_hw and hns_nic_net_xmit.

## References
- http://www.securityfocus.com/bid/103277
- https://www.debian.org/security/2018/dsa-4188
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=27463ad99f738ed93c7c8b3e2e5bc8c4853a2ff2
- https://github.com/torvalds/linux/commit/27463ad99f738ed93c7c8b3e2e5bc8c4853a2ff2
