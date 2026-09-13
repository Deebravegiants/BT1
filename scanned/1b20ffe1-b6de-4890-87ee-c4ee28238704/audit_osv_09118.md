# [M] CVE-2016-7994

## Summary
Severity: Medium
Advisory: CVE-2016-7994
CVSS: 6.0 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2016-12-10
Source: https://osv.dev/vulnerability/CVE-2016-7994
Type: osv

## Details
Memory leak in the virtio_gpu_resource_create_2d function in hw/display/virtio-gpu.c in QEMU (aka Quick Emulator) allows local guest OS administrators to cause a denial of service (memory consumption) via a large number of VIRTIO_GPU_CMD_RESOURCE_CREATE_2D commands.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00140.html
- http://www.openwall.com/lists/oss-security/2016/10/07/2
- http://www.openwall.com/lists/oss-security/2016/10/08/3
- http://www.securityfocus.com/bid/93453
- https://security.gentoo.org/glsa/201611-11
- https://lists.gnu.org/archive/html/qemu-devel/2016-09/msg04083.html
