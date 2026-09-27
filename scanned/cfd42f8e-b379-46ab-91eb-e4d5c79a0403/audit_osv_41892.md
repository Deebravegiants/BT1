# [H] drm/msm/dpu: don't mix devm and drmm functions

## Summary
Severity: High
Advisory: CVE-2026-64050
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64050
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dpu: don't mix devm and drmm functions

Mixing devm and drmm functions will result in a use-after-free on msm
driver teardown if userspace keeps a reference on the drm device:
The WB connector data will be destroyed because of the use of
devm_kzalloc()), while the usersoace still can try interacting with the
WB connector (which uses drmm_ functions).

Change dpu_writeback_init() to use drmm_.

Patchwork: https://patchwork.freedesktop.org/patch/722656/

## References
- https://git.kernel.org/stable/c/95048a12f48c627bc2ccc4d84f87640630ba2bdb
- https://git.kernel.org/stable/c/c0c70a11365cba7fba25a77463582bcec0f7846e
- https://git.kernel.org/stable/c/ff58e5ef1b46ce614af048d2d04986df05ffab90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64050.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64050
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
