# [M] drm/xe/oa: Fix "Missing outer runtime PM protection" warning

## Summary
Severity: Medium
Advisory: CVE-2024-53132
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-04
Source: https://osv.dev/vulnerability/CVE-2024-53132
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/oa: Fix "Missing outer runtime PM protection" warning

Fix the following drm_WARN:

[953.586396] xe 0000:00:02.0: [drm] Missing outer runtime PM protection
...
<4> [953.587090]  ? xe_pm_runtime_get_noresume+0x8d/0xa0 [xe]
<4> [953.587208]  guc_exec_queue_add_msg+0x28/0x130 [xe]
<4> [953.587319]  guc_exec_queue_fini+0x3a/0x40 [xe]
<4> [953.587425]  xe_exec_queue_destroy+0xb3/0xf0 [xe]
<4> [953.587515]  xe_oa_release+0x9c/0xc0 [xe]

(cherry picked from commit b107c63d2953907908fd0cafb0e543b3c3167b75)

## References
- https://git.kernel.org/stable/c/c0403e4ceecaefbeaf78263dffcd3e3f06a19f6b
- https://git.kernel.org/stable/c/ed7cd3510d8da6e3578d9125a9ea4440f8adeeaa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53132.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
