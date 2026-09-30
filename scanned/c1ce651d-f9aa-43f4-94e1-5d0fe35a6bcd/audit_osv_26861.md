# [H] drm/i915: fix race condition UAF in i915_perf_add_config_ioctl

## Summary
Severity: High
Advisory: CVE-2023-54202
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54202
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.15.108, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/i915: fix race condition UAF in i915_perf_add_config_ioctl

Userspace can guess the id value and try to race oa_config object creation
with config remove, resulting in a use-after-free if we dereference the
object after unlocking the metrics_lock.  For that reason, unlocking the
metrics_lock must be done after we are done dereferencing the object.

[tursulin: Manually added stable tag.]
(cherry picked from commit 49f6f6483b652108bcb73accd0204a464b922395)

## References
- https://git.kernel.org/stable/c/240b1502708858b5e3f10b6dc5ca3f148a322fef
- https://git.kernel.org/stable/c/6eeb1cba4c9dc47656ea328afa34953c28783d8c
- https://git.kernel.org/stable/c/7eb98f5ac551863efe8be810cea1cd5411d677b1
- https://git.kernel.org/stable/c/dc30c011469165d57af9adac5baff7d767d20e5c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54202.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54202
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
