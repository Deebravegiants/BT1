# [M] CVE-2020-36158

## Summary
Severity: Medium
Advisory: CVE-2020-36158
Aliases: A-177123726, PUB-A-177123726
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-05
Source: https://osv.dev/vulnerability/CVE-2020-36158
Type: osv

## Details
mwifiex_cmd_802_11_ad_hoc_start in drivers/net/wireless/marvell/mwifiex/join.c in the Linux kernel through 5.10.4 might allow remote attackers to execute arbitrary code via a long SSID value, aka CID-5c455c5ab332.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HCHBIRS27VMOGMBHPWP2R7SZRFXT6O6U/
- https://patchwork.kernel.org/project/linux-wireless/patch/20201206084801.26479-1-ruc_zhangxiaohui%40163.com/
- https://lore.kernel.org/r/20201206084801.26479-1-ruc_zhangxiaohui%40163.com
- https://lists.debian.org/debian-lts-announce/2021/02/msg00018.html
- https://lists.debian.org/debian-lts-announce/2021/03/msg00010.html
- https://security.netapp.com/advisory/ntap-20210212-0002/
- https://www.debian.org/security/2021/dsa-4843
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5c455c5ab332773464d02ba17015acdca198f03d
- https://github.com/torvalds/linux/commit/5c455c5ab332773464d02ba17015acdca198f03d
