# [H] CVE-2022-41674

## Summary
Severity: High
Advisory: CVE-2022-41674
Aliases: A-253641805, ASB-A-253641805
CVSS: 8.1 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-41674
Type: osv

## Details
An issue was discovered in the Linux kernel before 5.19.16. Attackers able to inject WLAN frames could cause a buffer overflow in the ieee80211_bss_info_update function in net/mac80211/scan.c.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/net/mac80211/scan.c
- https://www.debian.org/security/2022/dsa-5257
- http://packetstormsecurity.com/files/169951/Kernel-Live-Patch-Security-Notice-LSN-0090-1.html
- http://www.openwall.com/lists/oss-security/2022/10/13/2
- https://git.kernel.org/pub/scm/linux/kernel/git/wireless/wireless.git/commit/?id=aebe9f4639b13a1f4e9a6b42cdd2e38c617b442d
- https://bugzilla.suse.com/show_bug.cgi?id=1203770
- https://www.openwall.com/lists/oss-security/2022/10/13/5
