# [M] CVE-2018-21008

## Summary
Severity: Medium
Advisory: CVE-2018-21008
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-09-04
Source: https://osv.dev/vulnerability/CVE-2018-21008
Type: osv

## Details
An issue was discovered in the Linux kernel before 4.16.7. A use-after-free can be caused by the function rsi_mac80211_detach in the file drivers/net/wireless/rsi/rsi_91x_mac80211.c.

## References
- https://usn.ubuntu.com/4162-1/
- https://usn.ubuntu.com/4162-2/
- https://usn.ubuntu.com/4163-1/
- http://packetstormsecurity.com/files/154951/Kernel-Live-Patch-Security-Notice-LSN-0058-1.html
- https://usn.ubuntu.com/4163-2/
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00064.html
- http://lists.opensuse.org/opensuse-security-announce/2019-09/msg00066.html
- https://lists.debian.org/debian-lts-announce/2019/09/msg00025.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.16.7
- https://security.netapp.com/advisory/ntap-20191004-0001/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=abd39c6ded9db53aa44c2540092bdd5fb6590fa8
