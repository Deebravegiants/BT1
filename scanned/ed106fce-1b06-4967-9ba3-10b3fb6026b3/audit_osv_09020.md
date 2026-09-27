# [M] CVE-2016-7422

## Summary
Severity: Medium
Advisory: CVE-2016-7422
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7422
Type: osv

## Details
The virtqueue_map_desc function in hw/virtio/virtio.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (NULL pointer dereference and QEMU process crash) via a large I/O descriptor buffer length value.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=973e7170dddefb491a48df5cba33b2ae151013a0
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/09/16/10
- http://www.openwall.com/lists/oss-security/2016/09/16/4
- http://www.securityfocus.com/bid/92996
- https://access.redhat.com/errata/RHSA-2017:2392
- https://access.redhat.com/errata/RHSA-2017:2408
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg03546.html
