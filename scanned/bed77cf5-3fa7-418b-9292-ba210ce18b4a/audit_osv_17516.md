# [M] CVE-2020-15863

## Summary
Severity: Medium
Advisory: CVE-2020-15863
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-07-28
Source: https://osv.dev/vulnerability/CVE-2020-15863
Type: osv

## Details
hw/net/xgmac.c in the XGMAC Ethernet controller in QEMU before 07-20-2020 has a buffer overflow. This occurs during packet transmission and affects the highbank and midway emulated machines. A guest user or process could use this flaw to crash the QEMU process on the host, resulting in a denial of service or potential privileged code execution. This was fixed in commit 5519724a13664b43e225ca05351c60b4468e4555.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commitdiff%3Bh=5519724a13664b43e225ca05351c60b4468e4555
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00024.html
- https://security.gentoo.org/glsa/202208-27
- https://usn.ubuntu.com/4467-1/
- https://www.debian.org/security/2020/dsa-4760
- http://www.openwall.com/lists/oss-security/2020/07/22/1
- https://lists.nongnu.org/archive/html/qemu-devel/2020-07/msg03497.html
- https://lists.nongnu.org/archive/html/qemu-devel/2020-07/msg05745.html
