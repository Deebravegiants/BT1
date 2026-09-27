# [H] CVE-2015-7504

## Summary
Severity: High
Advisory: CVE-2015-7504
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-10-16
Source: https://osv.dev/vulnerability/CVE-2015-7504
Type: osv

## Details
Heap-based buffer overflow in the pcnet_receive function in hw/net/pcnet.c in QEMU allows guest OS administrators to cause a denial of service (instance crash) or possibly execute arbitrary code via a series of packets in loopback mode.

## References
- http://rhn.redhat.com/errata/RHSA-2015-2694.html
- http://rhn.redhat.com/errata/RHSA-2015-2695.html
- http://rhn.redhat.com/errata/RHSA-2015-2696.html
- http://www.debian.org/security/2016/dsa-3469
- http://www.debian.org/security/2016/dsa-3470
- http://www.debian.org/security/2016/dsa-3471
- http://www.openwall.com/lists/oss-security/2015/11/30/2
- http://www.securityfocus.com/bid/78227
- http://www.securitytracker.com/id/1034268
- http://xenbits.xen.org/xsa/advisory-162.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-11/msg06342.html
- https://security.gentoo.org/glsa/201602-01
- https://security.gentoo.org/glsa/201604-03
- http://www.openwall.com/lists/oss-security/2015/11/30/2
- https://lists.gnu.org/archive/html/qemu-devel/2015-11/msg06342.html
- http://www.openwall.com/lists/oss-security/2015/11/30/2
- http://xenbits.xen.org/xsa/advisory-162.html
- https://lists.gnu.org/archive/html/qemu-devel/2015-11/msg06342.html
- https://security.gentoo.org/glsa/201602-01
- https://security.gentoo.org/glsa/201604-03
