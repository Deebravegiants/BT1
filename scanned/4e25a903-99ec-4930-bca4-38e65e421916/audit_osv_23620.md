# [M] drm/amd/display: Fix a NULL pointer dereference in amdgpu_dm_connector_add_common_modes()

## Summary
Severity: Medium
Advisory: CVE-2022-49232
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49232
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix a NULL pointer dereference in amdgpu_dm_connector_add_common_modes()

In amdgpu_dm_connector_add_common_modes(), amdgpu_dm_create_common_mode()
is assigned to mode and is passed to drm_mode_probed_add() directly after
that. drm_mode_probed_add() passes &mode->head to list_add_tail(), and
there is a dereference of it in list_add_tail() without recoveries, which
could lead to NULL pointer dereference on failure of
amdgpu_dm_create_common_mode().

Fix this by adding a NULL check of mode.

This bug was found by a static analyzer.

Builds with 'make allyesconfig' show no new warnings,
and our static analyzer no longer warns about this code.

## References
- https://git.kernel.org/stable/c/19a7eba284790cfbba2945deb2363cf03ce41648
- https://git.kernel.org/stable/c/2c729dec8c1e3e2892fde5ce8181553860914e74
- https://git.kernel.org/stable/c/57f4ad5e286fe4599c8fc63cf89f85f9eec7f9c9
- https://git.kernel.org/stable/c/588a70177df3b1777484267584ef38ab2ca899a2
- https://git.kernel.org/stable/c/639b3b9def0a6a3f316a195d705d14113236e89c
- https://git.kernel.org/stable/c/bdc7429708a0772d90c208975694f7c2133b1202
- https://git.kernel.org/stable/c/f4eaa999fec78dec2a9c2d797438e05cbffb125b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49232.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
