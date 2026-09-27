# [M] CVE-2016-7421

## Summary
Severity: Medium
Advisory: CVE-2016-7421
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7421
Type: osv

## Details
The pvscsi_ring_pop_req_descr function in hw/scsi/vmw_pvscsi.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) by leveraging failure to limit process IO loop to the ring size.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=d251157ac1928191af851d199a9ff255d330bec9
- http://www.openwall.com/lists/oss-security/2016/09/16/3
- http://www.openwall.com/lists/oss-security/2016/09/16/9
- http://www.securityfocus.com/bid/92998
- https://lists.debian.org/debian-lts-announce/2018/11/msg00038.html
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg03609.html
