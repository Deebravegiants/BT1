# [H] drm/amdkfd: Use dynamic allocation for CU occupancy array in 'kfd_get_cu_occupancy()'

## Summary
Severity: High
Advisory: CVE-2024-56695
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56695
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Use dynamic allocation for CU occupancy array in 'kfd_get_cu_occupancy()'

The `kfd_get_cu_occupancy` function previously declared a large
`cu_occupancy` array as a local variable, which could lead to stack
overflows due to excessive stack usage. This commit replaces the static
array allocation with dynamic memory allocation using `kcalloc`,
thereby reducing the stack size.

This change avoids the risk of stack overflows in kernel space,  in
scenarios where `AMDGPU_MAX_QUEUES` is large. The  allocated memory is
freed using `kfree` before the function returns  to prevent memory
leaks.

Fixes the below with gcc W=1:
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_process.c: In function ‘kfd_get_cu_occupancy’:
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_process.c:322:1: warning: the frame size of 1056 bytes is larger than 1024 bytes [-Wframe-larger-than=]
  322 | }
      | ^

## References
- https://git.kernel.org/stable/c/6d9f07196389f35a3afebcf1a12c1425725caddd
- https://git.kernel.org/stable/c/922f0e00017b09d9d47e3efac008c8b20ed546a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56695.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56695
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
