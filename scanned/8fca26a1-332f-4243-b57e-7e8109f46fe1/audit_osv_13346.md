# [M] CVE-2018-19489

## Summary
Severity: Medium
Advisory: CVE-2018-19489
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-13
Source: https://osv.dev/vulnerability/CVE-2018-19489
Type: osv

## Details
v9fs_wstat in hw/9pfs/9p.c in QEMU allows guest OS users to cause a denial of service (crash) because of a race condition during file renaming.

## References
- https://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=1d20398694a3b67a388d955b7a945ba4aa90a8a8
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGCFIFSIWUREEQQOZDZFBYKWZHXCWBZN/
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00042.html
- http://www.securityfocus.com/bid/106007
- https://exchange.xforce.ibmcloud.com/vulnerabilities/153326
- https://lists.debian.org/debian-lts-announce/2019/01/msg00023.html
- https://seclists.org/bugtraq/2019/May/76
- https://security-tracker.debian.org/tracker/CVE-2018-19489
- https://usn.ubuntu.com/3923-1/
- https://www.debian.org/security/2019/dsa-4454
- http://www.openwall.com/lists/oss-security/2018/11/26/1
- https://lists.gnu.org/archive/html/qemu-devel/2018-11/msg04489.html
