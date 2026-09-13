# [H] drm/mgag200: Bind I2C lifetime to DRM device

## Summary
Severity: High
Advisory: CVE-2024-44967
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-04
Source: https://osv.dev/vulnerability/CVE-2024-44967
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.105, >=6.2.0 <6.6.46, >=6.7.0 <6.10.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/mgag200: Bind I2C lifetime to DRM device

Managed cleanup with devm_add_action_or_reset() will release the I2C
adapter when the underlying Linux device goes away. But the connector
still refers to it, so this cleanup leaves behind a stale pointer
in struct drm_connector.ddc.

Bind the lifetime of the I2C adapter to the connector's lifetime by
using DRM's managed release. When the DRM device goes away (after
the Linux device) DRM will first clean up the connector and then
clean up the I2C adapter.

## References
- https://git.kernel.org/stable/c/55a6916db77102765b22855d3a0add4751988b7c
- https://git.kernel.org/stable/c/81d34df843620e902dd04aa9205c875833d61c17
- https://git.kernel.org/stable/c/9d96b91e03cba9dfcb4ac370c93af4dbc47d5191
- https://git.kernel.org/stable/c/eb1ae34e48a09b7a1179c579aed042b032e408f4
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/44xxx/CVE-2024-44967.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-44967
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
