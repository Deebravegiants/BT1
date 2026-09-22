# [M] drm/client: Fix memory leak in drm_client_modeset_probe

## Summary
Severity: Medium
Advisory: CVE-2023-53288
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53288
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <5.4.251, >=5.5.0 <5.10.188, >=5.11.0 <5.15.123, >=5.16.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/client: Fix memory leak in drm_client_modeset_probe

When a new mode is set to modeset->mode, the previous mode should be freed.
This fixes the following kmemleak report:

drm_mode_duplicate+0x45/0x220 [drm]
drm_client_modeset_probe+0x944/0xf50 [drm]
__drm_fb_helper_initial_config_and_unlock+0xb4/0x2c0 [drm_kms_helper]
drm_fbdev_client_hotplug+0x2bc/0x4d0 [drm_kms_helper]
drm_client_register+0x169/0x240 [drm]
ast_pci_probe+0x142/0x190 [ast]
local_pci_probe+0xdc/0x180
work_for_cpu_fn+0x4e/0xa0
process_one_work+0x8b7/0x1540
worker_thread+0x70a/0xed0
kthread+0x29f/0x340
ret_from_fork+0x1f/0x30

## References
- https://git.kernel.org/stable/c/1369d0c586ad44f2d18fe2f4cbc5bcb24132fa71
- https://git.kernel.org/stable/c/2329cc7a101af1a844fbf706c0724c0baea38365
- https://git.kernel.org/stable/c/5d580017bdb9b3e930b6009e467e5e1589f8ca8a
- https://git.kernel.org/stable/c/5f2a12f64347f535c6ef55fa7eb36a2874d69b59
- https://git.kernel.org/stable/c/8108a494639e56aea77e7196a1d6ea89792b9d4a
- https://git.kernel.org/stable/c/917bef37cfaca07781c6fbaf6cd9404d27e64e6f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53288.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
