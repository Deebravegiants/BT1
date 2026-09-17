# [M] drm/msm/dp: fix aux-bus EP lifetime

## Summary
Severity: Medium
Advisory: CVE-2022-50360
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2022-50360
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dp: fix aux-bus EP lifetime

Device-managed resources allocated post component bind must be tied to
the lifetime of the aggregate DRM device or they will not necessarily be
released when binding of the aggregate device is deferred.

This can lead resource leaks or failure to bind the aggregate device
when binding is later retried and a second attempt to allocate the
resources is made.

For the DP aux-bus, an attempt to populate the bus a second time will
simply fail ("DP AUX EP device already populated").

Fix this by tying the lifetime of the EP device to the DRM device rather
than DP controller platform device.

Patchwork: https://patchwork.freedesktop.org/patch/502672/

## References
- https://git.kernel.org/stable/c/2b57f726611e294dc4297dd48eb8c98ef1938e82
- https://git.kernel.org/stable/c/8768663188e4169333f66583e4d2432e65c421df
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50360.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50360
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
