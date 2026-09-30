# [M] CVE-2016-7909

## Summary
Severity: Medium
Advisory: CVE-2016-7909
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-05
Source: https://osv.dev/vulnerability/CVE-2016-7909
Type: osv

## Details
The pcnet_rdra_addr function in hw/net/pcnet.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) by setting the (1) receive or (2) transmit descriptor ring length to 0.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/03/3
- http://www.openwall.com/lists/oss-security/2016/10/03/6
- http://www.securityfocus.com/bid/93275
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg07942.html
