# [M] CVE-2022-42722

## Summary
Severity: Medium
Advisory: CVE-2022-42722
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-10-14
Source: https://osv.dev/vulnerability/CVE-2022-42722
Type: osv

## Details
In the Linux kernel 5.8 through 5.19.x before 5.19.16, local attackers able to inject WLAN frames into the mac80211 stack could cause a NULL pointer dereference denial-of-service attack against the beacon protection of P2P devices.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://security.netapp.com/advisory/ntap-20230203-0008/
- https://www.debian.org/security/2022/dsa-5257
- http://packetstormsecurity.com/files/169951/Kernel-Live-Patch-Security-Notice-LSN-0090-1.html
- https://lists.debian.org/debian-lts-announce/2022/11/msg00001.html
- https://bugzilla.suse.com/show_bug.cgi?id=1204125
- https://git.kernel.org/pub/scm/linux/kernel/git/wireless/wireless.git/commit/?id=b2d03cabe2b2e150ff5a381731ea0355459be09f
- http://www.openwall.com/lists/oss-security/2022/10/13/5
