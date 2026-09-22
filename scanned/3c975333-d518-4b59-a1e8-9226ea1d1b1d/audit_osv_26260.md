# [H] drm/vmwgfx: fix a memleak in vmw_gmrid_man_get_node

## Summary
Severity: High
Advisory: CVE-2023-52662
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2023-52662
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: fix a memleak in vmw_gmrid_man_get_node

When ida_alloc_max fails, resources allocated before should be freed,
including *res allocated by kmalloc and ttm_resource_init.

## References
- https://git.kernel.org/stable/c/03b1072616a8f7d6e8594f643b416a9467c83fbf
- https://git.kernel.org/stable/c/40624af6674745e174c754a20d7c53c250e65e7a
- https://git.kernel.org/stable/c/6fc6233f6db1579b69b54b44571f1a7fde8186e6
- https://git.kernel.org/stable/c/83e0f220d1e992fa074157fcf14945bf170ffbc5
- https://git.kernel.org/stable/c/89709105a6091948ffb6ec2427954cbfe45358ce
- https://git.kernel.org/stable/c/d1e546ab91c670e536a274a75481034ab7534876
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52662.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52662
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
