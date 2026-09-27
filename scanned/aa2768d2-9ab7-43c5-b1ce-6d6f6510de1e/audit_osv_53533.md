# [H] CVE-2022-47521

## Summary
Severity: High
Advisory: CVE-2022-47521
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47521
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.0.11. Missing validation of IEEE80211_P2P_ATTR_CHANNEL_LIST in drivers/net/wireless/microchip/wilc1000/cfg80211.c in the WILC1000 wireless driver can trigger a heap-based buffer overflow when parsing the operating channel attribute from Wi-Fi management frames.

## References
- https://lore.kernel.org/r/20221123153543.8568-4-philipturnbull%40github.com
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://security.netapp.com/advisory/ntap-20230113-0007/
- https://github.com/torvalds/linux/commit/f9b62f9843c7b0afdaecabbcebf1dbba18599408
