# [M] CVE-2017-5552

## Summary
Severity: Medium
Advisory: CVE-2017-5552
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-5552
Type: osv

## Details
Memory leak in the virgl_resource_attach_backing function in hw/display/virtio-gpu-3d.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (host memory consumption) via a large number of VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING commands.

## References
- http://git.qemu.org/?p=qemu.git%3Ba=commit%3Bh=33243031dad02d161225ba99d782616da133f689
- http://www.securityfocus.com/bid/95773
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/01/20/17
- http://www.openwall.com/lists/oss-security/2017/01/21/5
