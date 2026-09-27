# [M] drm/amd/amdgpu/amdgpu_cs: fix refcount leak of a dma_fence obj

## Summary
Severity: Medium
Advisory: CVE-2022-49137
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49137
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <4.19.238, >=4.20.0 <5.4.189, >=5.5.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/amdgpu/amdgpu_cs: fix refcount leak of a dma_fence obj

This issue takes place in an error path in
amdgpu_cs_fence_to_handle_ioctl(). When `info->in.what` falls into
default case, the function simply returns -EINVAL, forgetting to
decrement the reference count of a dma_fence obj, which is bumped
earlier by amdgpu_cs_get_fence(). This may result in reference count
leaks.

Fix it by decreasing the refcount of specific object before returning
the error code.

## References
- https://git.kernel.org/stable/c/3edd8646cb7c11b57c90e026bda6f21076223f5b
- https://git.kernel.org/stable/c/4009f104b02b223d1a11d74b36b1cc083bc37028
- https://git.kernel.org/stable/c/72d77ddb2224ebc00648f4f78f8a9a259dccbdf7
- https://git.kernel.org/stable/c/927beb05aaa429c883cc0ec6adc48964b187e291
- https://git.kernel.org/stable/c/b6d1f7d97c81ebaf2cda9c4c943ee2e484fffdcf
- https://git.kernel.org/stable/c/bc2d5c0775c839e2b072884f4ee6a93ba410f107
- https://git.kernel.org/stable/c/dfced44f122c500004a48ecc8db516bb6a295a1b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49137.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
