# [H] CVE-2022-42720

## Summary
Severity: High
Advisory: CVE-2022-42720
Aliases: A-253642015, ASB-A-253642015
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-42720
Type: osv

## Details
Various refcounting bugs in the multi-BSS handling in the mac80211 stack in the Linux kernel 5.1 through 5.19.x before 5.19.16 could be used by local attackers (able to inject WLAN frames) to trigger use-after-free conditions to potentially execute code.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- http://packetstormsecurity.com/files/169951/Kernel-Live-Patch-Security-Notice-LSN-0090-1.html
- https://security.netapp.com/advisory/ntap-20230203-0008/
- https://www.debian.org/security/2022/dsa-5257
- https://bugzilla.suse.com/show_bug.cgi?id=1204059
- https://git.kernel.org/pub/scm/linux/kernel/git/wireless/wireless.git/commit/?id=0b7808818cb9df6680f98996b8e9a439fa7bcc2f
- http://www.openwall.com/lists/oss-security/2022/10/13/5
