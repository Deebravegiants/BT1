# [M] CVE-2016-6490

## Summary
Severity: Medium
Advisory: CVE-2016-6490
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-6490
Type: osv

## Details
The virtqueue_map_desc function in hw/virtio/virtio.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (infinite loop and QEMU process crash) via a zero length for the descriptor buffer.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=1e7aed70144b4673fc26e73062064b6724795e5f
- http://www.openwall.com/lists/oss-security/2016/07/28/4
- http://www.openwall.com/lists/oss-security/2016/07/28/9
- https://security.gentoo.org/glsa/201609-01
- https://lists.gnu.org/archive/html/qemu-devel/2016-07/msg06246.html
