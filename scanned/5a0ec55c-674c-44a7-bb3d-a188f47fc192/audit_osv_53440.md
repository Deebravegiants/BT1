# [H] CVE-2022-42719

## Summary
Severity: High
Advisory: CVE-2022-42719
Aliases: A-253642087, ASB-A-253642087
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-13
Source: https://osv.dev/vulnerability/CVE-2022-42719
Type: osv

## Details
A use-after-free in the mac80211 stack when parsing a multi-BSSID element in the Linux kernel 5.2 through 5.19.x before 5.19.16 could be used by attackers (able to inject WLAN frames) to crash the kernel and potentially execute code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- http://packetstormsecurity.com/files/171005/Kernel-Live-Patch-Security-Notice-LNS-0091-1.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://security.netapp.com/advisory/ntap-20230203-0008/
- https://www.debian.org/security/2022/dsa-5257
- http://www.openwall.com/lists/oss-security/2022/10/13/2
- https://bugzilla.suse.com/show_bug.cgi?id=1204051
- https://git.kernel.org/pub/scm/linux/kernel/git/wireless/wireless.git/commit/?id=ff05d4b45dd89b922578dac497dcabf57cf771c6
- http://www.openwall.com/lists/oss-security/2022/10/13/5
