# [H] CVE-2023-31248

## Summary
Severity: High
Advisory: CVE-2023-31248
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-31248
Type: osv

## Details
Linux Kernel nftables Use-After-Free Local Privilege Escalation Vulnerability; `nft_chain_lookup_byid()` failed to check whether a chain was active and CAP_NET_ADMIN is in any user or network namespace

## References
- https://www.debian.org/security/2023/dsa-5453
- http://packetstormsecurity.com/files/174577/Kernel-Live-Patch-Security-Notice-LSN-0097-1.html
- http://www.openwall.com/lists/oss-security/2023/07/05/2
- https://lists.debian.org/debian-lts-announce/2023/08/msg00001.html
- https://security.netapp.com/advisory/ntap-20240201-0001/
- http://packetstormsecurity.com/files/173757/Kernel-Live-Patch-Security-Notice-LSN-0096-1.html
- https://lore.kernel.org/netfilter-devel/20230705121627.GC19489@breakpoint.cc/T/
- https://www.openwall.com/lists/oss-security/2023/07/05/2
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RGZC5XOANA75OJ4XARBBXYSLDKUIJI5E/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UPHI46ROSSLVAV4R5LJWJYU747JGOS6D/
