# [H] drm/exynos: vidi: use priv->vidi_dev for ctx lookup in vidi_connection_ioctl()

## Summary
Severity: High
Advisory: CVE-2026-45956
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45956
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/exynos: vidi: use priv->vidi_dev for ctx lookup in vidi_connection_ioctl()

vidi_connection_ioctl() retrieves the driver_data from drm_dev->dev to
obtain a struct vidi_context pointer. However, drm_dev->dev is the
exynos-drm master device, and the driver_data contained therein is not
the vidi component device, but a completely different device.

This can lead to various bugs, ranging from null pointer dereferences and
garbage value accesses to, in unlucky cases, out-of-bounds errors,
use-after-free errors, and more.

To resolve this issue, we need to store/delete the vidi device pointer in
exynos_drm_private->vidi_dev during bind/unbind, and then read this
exynos_drm_private->vidi_dev within ioctl() to obtain the correct
struct vidi_context pointer.

## References
- https://git.kernel.org/stable/c/21ca24ba51a2c28bcc4df9d7e5a40b0eb66ab76d
- https://git.kernel.org/stable/c/2987642c5213508c6c9e718324c0d5289a92c474
- https://git.kernel.org/stable/c/65d1213baffa363f2eb1117b1dc7acc573b890f8
- https://git.kernel.org/stable/c/875fa28690e93ed5296c31d3344556c6bb867234
- https://git.kernel.org/stable/c/a540f767642f75240a6c35f6a65b69e44cfcea9d
- https://git.kernel.org/stable/c/b5fc86d753dd4c281a943b92f0eef02d31af03d7
- https://git.kernel.org/stable/c/d3968a0d85b211e197f2f4f06268a7031079e0d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45956.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
