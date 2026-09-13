# [H] CVE-2022-47518

## Summary
Severity: High
Advisory: CVE-2022-47518
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-18
Source: https://osv.dev/vulnerability/CVE-2022-47518
Type: osv

## Details
An issue was discovered in the Linux kernel before 6.0.11. Missing validation of the number of channels in drivers/net/wireless/microchip/wilc1000/cfg80211.c in the WILC1000 wireless driver can trigger a heap-based buffer overflow when copying the list of operating channels from Wi-Fi management frames.

## References
- https://lore.kernel.org/r/20221123153543.8568-5-philipturnbull%40github.com
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://security.netapp.com/advisory/ntap-20230113-0007/
- https://github.com/torvalds/linux/commit/0cdfa9e6f0915e3d243e2393bfa8a22e12d553b0
