# [M] drm/panthor: avoid garbage value in panthor_ioctl_dev_query()

## Summary
Severity: Medium
Advisory: CVE-2025-21843
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-07
Source: https://osv.dev/vulnerability/CVE-2025-21843
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.13.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panthor: avoid garbage value in panthor_ioctl_dev_query()

'priorities_info' is uninitialized, and the uninitialized value is copied
to user object when calling PANTHOR_UOBJ_SET(). Using memset to initialize
'priorities_info' to avoid this garbage value problem.

## References
- https://git.kernel.org/stable/c/3b32b7f638fe61e9d29290960172f4e360e38233
- https://git.kernel.org/stable/c/64b95bbc08bacf3e4b05c8604e6a4fec43bb712a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21843.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21843
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
