# [M] CVE-2016-8910

## Summary
Severity: Medium
Advisory: CVE-2016-8910
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-11-04
Source: https://osv.dev/vulnerability/CVE-2016-8910
Type: osv

## Details
The rtl8139_cplus_transmit function in hw/net/rtl8139.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and CPU consumption) by leveraging failure to limit the ring descriptor count.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/24/5
- http://www.securityfocus.com/bid/93844
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201611-11
- http://www.openwall.com/lists/oss-security/2016/10/24/2
- https://lists.gnu.org/archive/html/qemu-devel/2016-10/msg05495.html
