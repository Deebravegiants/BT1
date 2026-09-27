# [H] drm/msm/dp: Drop aux devices together with DP controller

## Summary
Severity: High
Advisory: CVE-2023-53851
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53851
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dp: Drop aux devices together with DP controller

Using devres to depopulate the aux bus made sure that upon a probe
deferral the EDP panel device would be destroyed and recreated upon next
attempt.

But the struct device which the devres is tied to is the DPUs
(drm_dev->dev), which may be happen after the DP controller is torn
down.

Indications of this can be seen in the commonly seen EDID-hexdump full
of zeros in the log, or the occasional/rare KASAN fault where the
panel's attempt to read the EDID information causes a use after free on
DP resources.

It's tempting to move the devres to the DP controller's struct device,
but the resources used by the device(s) on the aux bus are explicitly
torn down in the error path. The KASAN-reported use-after-free also
remains, as the DP aux "module" explicitly frees its devres-allocated
memory in this code path.

As such, explicitly depopulate the aux bus in the error path, and in the
component unbind path, to avoid these issues.

Patchwork: https://patchwork.freedesktop.org/patch/542163/

## References
- https://git.kernel.org/stable/c/2fde37445807e6e6d7981402d0bf1be0e5d81291
- https://git.kernel.org/stable/c/a7bfb2ad2184a1fba78be35209b6019aa8cc8d4d
- https://git.kernel.org/stable/c/e09ed06938807cb113cddd0708ed74bd8cdaff33
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53851.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53851
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
