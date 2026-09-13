# [M] CVE-2016-7907

## Summary
Severity: Medium
Advisory: CVE-2016-7907
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-05
Source: https://osv.dev/vulnerability/CVE-2016-7907
Type: osv

## Details
The imx_fec_do_tx function in hw/net/imx_fec.c in QEMU (aka Quick Emulator) does not properly limit the buffer descriptor count when transmitting packets, which allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) via vectors involving a buffer descriptor with a length of 0 and crafted values in bd.flags.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/03/1
- http://www.openwall.com/lists/oss-security/2016/10/03/4
- http://www.securityfocus.com/bid/93274
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg05556.html
