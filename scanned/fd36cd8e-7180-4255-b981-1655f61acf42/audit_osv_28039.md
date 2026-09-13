# [M] drm/amd/display: fix NULL checks for adev->dm.dc in amdgpu_dm_fini()

## Summary
Severity: Medium
Advisory: CVE-2024-27041
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27041
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: fix NULL checks for adev->dm.dc in amdgpu_dm_fini()

Since 'adev->dm.dc' in amdgpu_dm_fini() might turn out to be NULL
before the call to dc_enable_dmub_notifications(), check
beforehand to ensure there will not be a possible NULL-ptr-deref
there.

Also, since commit 1e88eb1b2c25 ("drm/amd/display: Drop
CONFIG_DRM_AMD_DC_HDCP") there are two separate checks for NULL in
'adev->dm.dc' before dc_deinit_callbacks() and dc_dmub_srv_destroy().
Clean up by combining them all under one 'if'.

Found by Linux Verification Center (linuxtesting.org) with static
analysis tool SVACE.

## References
- https://git.kernel.org/stable/c/1c62697e4086de988b31124fb8c79c244ea05f2b
- https://git.kernel.org/stable/c/2a3cfb9a24a28da9cc13d2c525a76548865e182c
- https://git.kernel.org/stable/c/ca2eb375db76fd50f31afdd67d6ca4f833254957
- https://git.kernel.org/stable/c/e040f1fbe9abae91b12b074cfc3bbb5367b79811
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27041.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27041
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
