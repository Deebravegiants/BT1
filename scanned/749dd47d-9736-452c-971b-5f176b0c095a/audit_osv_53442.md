# [M] CVE-2022-42721

## Summary
Severity: Medium
Advisory: CVE-2022-42721
Aliases: A-253642088, ASB-A-253642088
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-42721
Type: osv

## Details
A list management bug in BSS handling in the mac80211 stack in the Linux kernel 5.1 through 5.19.x before 5.19.16 could be used by local attackers (able to inject WLAN frames) to corrupt a linked list and, in turn, potentially execute code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://security.netapp.com/advisory/ntap-20230203-0008/
- https://www.debian.org/security/2022/dsa-5257
- http://packetstormsecurity.com/files/169951/Kernel-Live-Patch-Security-Notice-LSN-0090-1.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://bugzilla.suse.com/show_bug.cgi?id=1204060
- https://git.kernel.org/pub/scm/linux/kernel/git/wireless/wireless.git/commit/?id=bcca852027e5878aec911a347407ecc88d6fff7f
- http://www.openwall.com/lists/oss-security/2022/10/13/5
