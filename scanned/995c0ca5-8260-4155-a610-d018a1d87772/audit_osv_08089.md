# [M] CVE-2016-10214

## Summary
Severity: Medium
Advisory: CVE-2016-10214
CVSS: 6.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-03-20
Source: https://osv.dev/vulnerability/CVE-2016-10214
Type: osv

## Details
Memory leak in the virgl_resource_attach_backing function in virglrenderer before 0.6.0 allows local guest OS users to cause a denial of service (memory consumption) via a large number of VIRTIO_GPU_CMD_RESOURCE_ATTACH_BACKING commands.

## References
- http://www.securityfocus.com/bid/96181
- https://security.gentoo.org/glsa/201707-06
- http://www.openwall.com/lists/oss-security/2017/02/09/5
- https://cgit.freedesktop.org/virglrenderer/commit/?id=40b0e7813325b08077b6f541b3989edb2d86d837
- https://lists.freedesktop.org/archives/virglrenderer-devel/2017-February/000145.html
