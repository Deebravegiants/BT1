# [M] drm/amdgpu: Fix the memory allocation issue in amdgpu_discovery_get_nps_info()

## Summary
Severity: Medium
Advisory: CVE-2024-56697
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56697
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: Fix the memory allocation issue in amdgpu_discovery_get_nps_info()

Fix two issues with memory allocation in amdgpu_discovery_get_nps_info()
for mem_ranges:

 - Add a check for allocation failure to avoid dereferencing a null
   pointer.

 - As suggested by Christophe, use kvcalloc() for memory allocation,
   which checks for multiplication overflow.

Additionally, assign the output parameters nps_type and range_cnt after
the kvcalloc() call to prevent modifying the output parameters in case
of an error return.

## References
- https://git.kernel.org/stable/c/a1144da794adedb9447437c57d69add56494309d
- https://git.kernel.org/stable/c/d14bea4e094871226ea69772d69dab8b7b5f4915
- https://git.kernel.org/stable/c/e8f1dbaa0437eba4e8c1d6a6d81eca2e2ce3d197
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56697.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
