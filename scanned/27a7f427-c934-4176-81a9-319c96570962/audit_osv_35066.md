# [H] drm/radeon: Remove calls to drm_put_dev()

## Summary
Severity: High
Advisory: CVE-2025-68181
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68181
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/radeon: Remove calls to drm_put_dev()

Since the allocation of the drivers main structure was changed to
devm_drm_dev_alloc() drm_put_dev()'ing to trigger it to be free'd
should be done by devres.

However, drm_put_dev() is still in the probe error and device remove
paths. When the driver fails to probe warnings like the following are
shown because devres is trying to drm_put_dev() after the driver
already did it.

[    5.642230] radeon 0000:01:05.0: probe with driver radeon failed with error -22
[    5.649605] ------------[ cut here ]------------
[    5.649607] refcount_t: underflow; use-after-free.
[    5.649620] WARNING: CPU: 0 PID: 357 at lib/refcount.c:28 refcount_warn_saturate+0xbe/0x110

(cherry picked from commit 3eb8c0b4c091da0a623ade0d3ee7aa4a93df1ea4)

## References
- https://git.kernel.org/stable/c/2fa41445d8c98f2a65503c373796466496edc0e7
- https://git.kernel.org/stable/c/745bae76acdd71709773c129a69deca01036250b
- https://git.kernel.org/stable/c/ec18f6b2c743cc471b2539ddb5caed20a012e640
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68181.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68181
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
