# [H] CVE-2021-47063

## Summary
Severity: High
Advisory: CVE-2021-47063
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47063
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: bridge/panel: Cleanup connector on bridge detach

If we don't call drm_connector_cleanup() manually in
panel_bridge_detach(), the connector will be cleaned up with the other
DRM objects in the call to drm_mode_config_cleanup(). However, since our
drm_connector is devm-allocated, by the time drm_mode_config_cleanup()
will be called, our connector will be long gone. Therefore, the
connector must be cleaned up when the bridge is detached to avoid
use-after-free conditions.

v2: Cleanup connector only if it was created

v3: Add FIXME

v4: (Use connector->dev) directly in if() block

## References
- https://git.kernel.org/stable/c/18149b420c9bd93c443e8d1f48a063d71d9f6aa1
- https://git.kernel.org/stable/c/4d906839d321c2efbf3fed4bc31ffd9ff55b75c0
- https://git.kernel.org/stable/c/98d7d76a74e48ec3ddf2e23950adff7edcab9327
- https://git.kernel.org/stable/c/ce450934a00cf896e648fde08d0bd1426653d7a2
