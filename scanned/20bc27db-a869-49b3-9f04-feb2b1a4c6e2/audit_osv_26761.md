# [H] amdgpu: validate offset_in_bo of drm_amdgpu_gem_va

## Summary
Severity: High
Advisory: CVE-2023-53819
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53819
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.313, >=4.20.0 <5.4.275, >=5.5.0 <5.10.188, >=5.11.0 <5.15.121, >=5.16.0 <6.1.39, >=6.2.0 <6.3.13, >=6.4.0 <6.4.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

amdgpu: validate offset_in_bo of drm_amdgpu_gem_va

This is motivated by OOB access in amdgpu_vm_update_range when
offset_in_bo+map_size overflows.

v2: keep the validations in amdgpu_vm_bo_map
v3: add the validations to amdgpu_vm_bo_map/amdgpu_vm_bo_replace_map
    rather than to amdgpu_gem_va_ioctl

## References
- https://git.kernel.org/stable/c/4300a47e4017c9febb60ffa7d39723eeaed00f2b
- https://git.kernel.org/stable/c/82aace80cfaab778245bd2f9e31b67953725e4d0
- https://git.kernel.org/stable/c/968e27fd037ec4732068820a9b9836eccc0e0a12
- https://git.kernel.org/stable/c/9f0bcf49e9895cb005d78b33a5eebfa11711b425
- https://git.kernel.org/stable/c/b10db1d2137415e5e7f9706d96cfe77539c499d4
- https://git.kernel.org/stable/c/bc6dbf34dc4fb639522f3e8e66ef05997c0441ee
- https://git.kernel.org/stable/c/d83c337e654d58d3edd15a2ae76e87dc601c07d9
- https://git.kernel.org/stable/c/f015aadc0d973047f49526a127e900c488d4e425
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53819.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53819
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
