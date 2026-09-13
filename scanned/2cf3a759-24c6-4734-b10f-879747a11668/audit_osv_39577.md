# [H] drm/amdkfd: validate SVM ioctl nattr against buffer size

## Summary
Severity: High
Advisory: CVE-2026-46197
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46197
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.90, >=6.13.0 <6.18.32, >=6.19.0 <7.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: validate SVM ioctl nattr against buffer size

Validate nattr field against the buffer size, preventing
out-of-bounds buffer access via user-controlled attribute count.

(cherry picked from commit 5eca8bfdfa456c3304ca77523718fe24254c172f)

## References
- https://git.kernel.org/stable/c/045e0ff208f0838a246c10204105126611b267a1
- https://git.kernel.org/stable/c/6abd3a4417cb73a7d0db7e25bf11fae1074bdba3
- https://git.kernel.org/stable/c/91c6dc5a41695d02dfc6299f106ac38a6c493e52
- https://git.kernel.org/stable/c/ccd060b5c7cc75ae7e211c250b97c5b6272e7efc
- https://git.kernel.org/stable/c/daa8bc5f83814b55b71d2b5b3a090d57a5219c21
- https://git.kernel.org/stable/c/db9530a9873a7c85d2266a922589ebcf427fa631
- https://git.kernel.org/stable/c/fb07a0c9c8419164812e07274947f11b1d92dd61
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46197.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46197
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
