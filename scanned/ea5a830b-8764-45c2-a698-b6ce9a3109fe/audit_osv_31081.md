# [M] drm/amd/display: Add check for granularity in dml ceil/floor helpers

## Summary
Severity: Medium
Advisory: CVE-2024-57922
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-19
Source: https://osv.dev/vulnerability/CVE-2024-57922
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.4.290, >=5.5.0 <5.10.234, >=5.11.0 <5.15.177, >=5.16.0 <6.1.125, >=6.2.0 <6.6.72, >=6.7.0 <6.12.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Add check for granularity in dml ceil/floor helpers

[Why]
Wrapper functions for dcn_bw_ceil2() and dcn_bw_floor2()
should check for granularity is non zero to avoid assert and
divide-by-zero error in dcn_bw_ functions.

[How]
Add check for granularity 0.

(cherry picked from commit f6e09701c3eb2ccb8cb0518e0b67f1c69742a4ec)

## References
- https://git.kernel.org/stable/c/0881fbc4fd62e00a2b8e102725f76d10351b2ea8
- https://git.kernel.org/stable/c/497471baf53bb8fd3cd1529d65d4d7f7b81f1917
- https://git.kernel.org/stable/c/4f0dd09ed3001725ffd8cdc2868e71df585392fe
- https://git.kernel.org/stable/c/8a9315e6f7b2d94c65a1ba476481deddb20fc3ae
- https://git.kernel.org/stable/c/95793f9684e58d2aa56671b2d616b4f9f577a0a8
- https://git.kernel.org/stable/c/ae9ab63a268be99a27a4720ca24f6be801744fee
- https://git.kernel.org/stable/c/f3d1e4062ef251fa55ccfeca1e54a98b6818b3a1
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57922.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57922
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
