# [M] drm/mediatek: dp: Only trigger DRM HPD events if bridge is attached

## Summary
Severity: Medium
Advisory: CVE-2023-53389
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53389
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mediatek: dp: Only trigger DRM HPD events if bridge is attached

The MediaTek DisplayPort interface bridge driver starts its interrupts
as soon as its probed. However when the interrupts trigger the bridge
might not have been attached to a DRM device. As drm_helper_hpd_irq_event()
does not check whether the passed in drm_device is valid or not, a NULL
pointer passed in results in a kernel NULL pointer dereference in it.

Check whether the bridge is attached and only trigger an HPD event if
it is.

## References
- https://git.kernel.org/stable/c/3551789d0635dfb2df8ab8e7fdbf0647e9c1724c
- https://git.kernel.org/stable/c/36b617f7e4ae663fcadd202ea061ca695ca75539
- https://git.kernel.org/stable/c/6524d3d58797975cc40b85be1e9b89721b4e8d0b
- https://git.kernel.org/stable/c/d1c04e338016ae2517c641806a831b1f3eee2bed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53389.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53389
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
