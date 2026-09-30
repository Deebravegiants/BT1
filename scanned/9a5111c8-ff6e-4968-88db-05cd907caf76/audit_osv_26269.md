# [H] drm/amdkfd: Confirm list is non-empty before utilizing list_first_entry in kfd_topology.c

## Summary
Severity: High
Advisory: CVE-2023-52678
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52678
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Confirm list is non-empty before utilizing list_first_entry in kfd_topology.c

Before using list_first_entry, make sure to check that list is not
empty, if list is empty return -ENODATA.

Fixes the below:
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_topology.c:1347 kfd_create_indirect_link_prop() warn: can 'gpu_link' even be NULL?
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_topology.c:1428 kfd_add_peer_prop() warn: can 'iolink1' even be NULL?
drivers/gpu/drm/amd/amdgpu/../amdkfd/kfd_topology.c:1433 kfd_add_peer_prop() warn: can 'iolink2' even be NULL?

## References
- https://git.kernel.org/stable/c/4525525cb7161d08f95d0e47025323dd10214313
- https://git.kernel.org/stable/c/499839eca34ad62d43025ec0b46b80e77065f6d8
- https://git.kernel.org/stable/c/4ac4e023ed7ab1c7c67d2d12b7b6198fcd099e5c
- https://git.kernel.org/stable/c/5024cce888e11e5688f77df81db9e14828495d64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52678.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52678
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
