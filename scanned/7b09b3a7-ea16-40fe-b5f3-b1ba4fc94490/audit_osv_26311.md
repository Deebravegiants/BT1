# [M] drm/amdgpu: Fix potential null pointer derefernce

## Summary
Severity: Medium
Advisory: CVE-2023-52814
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52814
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <5.10.202, >=5.11.0 <5.15.140, >=5.16.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix potential null pointer derefernce

The amdgpu_ras_get_context may return NULL if device
not support ras feature, so add check before using.

## References
- https://git.kernel.org/stable/c/80285ae1ec8717b597b20de38866c29d84d321a1
- https://git.kernel.org/stable/c/9b70fc7d70e8ef7c4a65034c9487f58609e708a1
- https://git.kernel.org/stable/c/b0702ee4d811708251cdf54d4a1d3e888d365111
- https://git.kernel.org/stable/c/b93a25de28af153312f0fc979b0663fc4bd3442b
- https://git.kernel.org/stable/c/c11cf5e117f50f5a767054600885acd981449afe
- https://git.kernel.org/stable/c/da46e63482fdc5e35c008865c22ac64027f6f0c2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52814.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52814
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
