# [H] drm/amdgpu: add missing size check in amdgpu_debugfs_gprwave_read()

## Summary
Severity: High
Advisory: CVE-2024-50282
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50282
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.324, >=4.20.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: add missing size check in amdgpu_debugfs_gprwave_read()

Avoid a possible buffer overflow if size is larger than 4K.

(cherry picked from commit f5d873f5825b40d886d03bd2aede91d4cf002434)

## References
- https://git.kernel.org/stable/c/2faaee36e6e30f9efc7fa6bcb0bdcbe05c23f51f
- https://git.kernel.org/stable/c/4d75b9468021c73108b4439794d69e892b1d24e3
- https://git.kernel.org/stable/c/673bdb4200c092692f83b5f7ba3df57021d52d29
- https://git.kernel.org/stable/c/8906728f2fbd6504cb488f4afdd66af28f330a7a
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50282.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50282
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
