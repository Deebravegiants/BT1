# [M] drm/sprd: fix potential NULL dereference

## Summary
Severity: Medium
Advisory: CVE-2022-49125
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49125
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/sprd: fix potential NULL dereference

'drm' could be null in sprd_drm_shutdown, and drm_warn maybe dereference
it, remove this warning log.


v1 -> v2:
- Split checking platform_get_resource() return value to a separate patch
- Use dev_warn() instead of removing the warning log

## References
- https://git.kernel.org/stable/c/8668658aebb0a19d877d5a81c004baf716c4aaa6
- https://git.kernel.org/stable/c/c3acc8db1bc221604e2db9807f01d8a44b97a64d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49125.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
