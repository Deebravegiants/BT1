# [M] CVE-2017-9060

## Summary
Severity: Medium
Advisory: CVE-2017-9060
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-01
Source: https://osv.dev/vulnerability/CVE-2017-9060
Type: osv

## Details
Memory leak in the virtio_gpu_set_scanout function in hw/display/virtio-gpu.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (memory consumption) via a large number of "VIRTIO_GPU_CMD_SET_SCANOUT:" commands.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=dd248ed7e204ee8a1873914e02b8b526e8f1b80d
- http://www.securityfocus.com/bid/98632
- https://security.gentoo.org/glsa/201706-03
- http://www.openwall.com/lists/oss-security/2017/05/19/1
- https://bugzilla.redhat.com/show_bug.cgi?id=1452597
