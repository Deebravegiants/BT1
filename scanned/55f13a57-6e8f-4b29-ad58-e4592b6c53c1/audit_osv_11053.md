# [M] CVE-2017-5857

## Summary
Severity: Medium
Advisory: CVE-2017-5857
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-16
Source: https://osv.dev/vulnerability/CVE-2017-5857
Type: osv

## Details
Memory leak in the virgl_cmd_resource_unref function in hw/display/virtio-gpu-3d.c in QEMU (aka Quick Emulator) allows local guest OS users to cause a denial of service (host memory consumption) via a large number of VIRTIO_GPU_CMD_RESOURCE_UNREF commands sent without detaching the backing storage beforehand.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=5e8e3c4c75c199aa1017db816fca02be2a9f8798
- http://www.securityfocus.com/bid/95993
- https://security.gentoo.org/glsa/201702-28
- http://www.openwall.com/lists/oss-security/2017/02/01/21
- http://www.openwall.com/lists/oss-security/2017/02/02/16
- https://bugzilla.redhat.com/show_bug.cgi?id=1418382
