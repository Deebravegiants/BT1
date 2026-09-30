# [M] drm/msm/dpu: Add a null ptr check for dpu_encoder_needs_modeset

## Summary
Severity: Medium
Advisory: CVE-2025-39820
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39820
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/dpu: Add a null ptr check for dpu_encoder_needs_modeset

The drm_atomic_get_new_connector_state() can return NULL if the
connector is not part of the atomic state. Add a check to prevent
a NULL pointer dereference.

This follows the same pattern used in dpu_encoder_update_topology()
within the same file, which checks for NULL before using conn_state.

Patchwork: https://patchwork.freedesktop.org/patch/665188/

## References
- https://git.kernel.org/stable/c/aaec54254b02f5959c3670177037464d828b2140
- https://git.kernel.org/stable/c/abebfed208515726760d79cf4f9f1a76b9a10a84
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39820.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39820
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
