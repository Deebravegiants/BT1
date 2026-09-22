# [H] CVE-2022-47519

## Summary
Severity: High
Advisory: CVE-2022-47519
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47519
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.0.11. Missing validation of IEEE80211_P2P_ATTR_OPER_CHANNEL in drivers/net/wireless/microchip/wilc1000/cfg80211.c in the WILC1000 wireless driver can trigger an out-of-bounds write when parsing the channel list attribute from Wi-Fi management frames.

## References
- https://lore.kernel.org/r/20221123153543.8568-3-philipturnbull%40github.com
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://security.netapp.com/advisory/ntap-20230113-0007/
- https://github.com/torvalds/linux/commit/051ae669e4505abbe05165bebf6be7922de11f41
