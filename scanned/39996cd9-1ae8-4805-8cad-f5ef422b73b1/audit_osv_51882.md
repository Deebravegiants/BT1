# [M] CVE-2021-43975

## Summary
Severity: Medium
Advisory: CVE-2021-43975
Aliases: A-207093880, PUB-A-207093880
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-43975
Type: osv

## Details
In the Linux kernel through 5.15.2, hw_atl_utils_fw_rpc_wait in drivers/net/ethernet/aquantia/atlantic/hw_atl/hw_atl_utils.c allows an attacker (who can introduce a crafted device) to trigger an out-of-bounds write via a crafted length value.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X24M7KDC4OJOZNS3RDSYC7ELNELOLQ2N/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YODMYMGZYDXQKGJGX7TJG4XV4L5YLLBD/
- https://lore.kernel.org/netdev/163698540868.13805.17800408021782408762.git-patchwork-notify%40kernel.org/T/
- https://lists.debian.org/debian-lts-announce/2022/03/msg00012.html
- https://security.netapp.com/advisory/ntap-20211210-0001/
- https://www.debian.org/security/2022/dsa-5096
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=b922f622592af76b57cbc566eaeccda0b31a3496
