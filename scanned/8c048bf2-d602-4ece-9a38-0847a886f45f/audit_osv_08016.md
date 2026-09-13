# [M] CVE-2016-10028

## Summary
Severity: Medium
Advisory: CVE-2016-10028
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-02-27
Source: https://osv.dev/vulnerability/CVE-2016-10028
Type: osv

## Details
The virgl_cmd_get_capset function in hw/display/virtio-gpu-3d.c in QEMU (aka Quick Emulator) built with Virtio GPU Device emulator support allows local guest OS users to cause a denial of service (out-of-bounds read and process crash) via a VIRTIO_GPU_CMD_GET_CAPSET command with a maximum capabilities size with a value of 0.

## References
- http://git.qemu-project.org/?p=qemu.git%3Ba=commit%3Bh=abd7f08b2353f43274b785db8c7224f082ef4d31
- http://www.securityfocus.com/bid/94981
- http://www.securitytracker.com/id/1037525
- https://security.gentoo.org/glsa/201701-49
- http://www.openwall.com/lists/oss-security/2016/12/20/1
- http://www.openwall.com/lists/oss-security/2016/12/22/14
- https://lists.gnu.org/archive/html/qemu-devel/2016-12/msg01903.html
