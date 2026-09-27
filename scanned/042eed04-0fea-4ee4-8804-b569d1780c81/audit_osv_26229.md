# [M] drm/amdgpu: Fix possible NULL dereference in amdgpu_ras_query_error_status_helper()

## Summary
Severity: Medium
Advisory: CVE-2023-52585
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-06
Source: https://osv.dev/vulnerability/CVE-2023-52585
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.7.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix possible NULL dereference in amdgpu_ras_query_error_status_helper()

Return invalid error code -EINVAL for invalid block id.

Fixes the below:

drivers/gpu/drm/amd/amdgpu/amdgpu_ras.c:1183 amdgpu_ras_query_error_status_helper() error: we previously assumed 'info' could be null (see line 1176)

## References
- https://git.kernel.org/stable/c/0eb296233f86750102aa43b97879b8d8311f249a
- https://git.kernel.org/stable/c/195a6289282e039024ad30ba66e6f94a4d0fbe49
- https://git.kernel.org/stable/c/467139546f3fb93913de064461b1a43a212d7626
- https://git.kernel.org/stable/c/7e6d6f27522bcd037856234b720ff607b9c4a09b
- https://git.kernel.org/stable/c/92cb363d16ac1e41c9764cdb513d0e89a6ff4915
- https://git.kernel.org/stable/c/b8d55a90fd55b767c25687747e2b24abd1ef8680
- https://git.kernel.org/stable/c/c364e7a34c85c2154fb2e47561965d5b5a0b69b1
- https://lists.debian.org/debian-lts-announce/2024/06/msg00019.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52585.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52585
- https://security.netapp.com/advisory/ntap-20240912-0009/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
