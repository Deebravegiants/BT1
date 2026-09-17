# [M] drm/msm/a6xx: Fix refcount leak in a6xx_gpu_init

## Summary
Severity: Medium
Advisory: CVE-2022-49462
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49462
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/msm/a6xx: Fix refcount leak in a6xx_gpu_init

of_parse_phandle() returns a node pointer with refcount
incremented, we should use of_node_put() on it when not need anymore.

a6xx_gmu_init() passes the node to of_find_device_by_node()
and of_dma_configure(), of_find_device_by_node() will takes its
reference, of_dma_configure() doesn't need the node after usage.

Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/06907a374f1b74f8f2fb30720dc6df81331e4fb5
- https://git.kernel.org/stable/c/48e82ce8cdb19c20a5020fa446b286d6a147450c
- https://git.kernel.org/stable/c/65ddbc0d26824e2a5d6154d01d8cf39344900213
- https://git.kernel.org/stable/c/6832e36f156ea35a6ed74bca72727806116effdd
- https://git.kernel.org/stable/c/c56de483093d7ad0782327f95dda7da97bc4c315
- https://git.kernel.org/stable/c/edff4c1af831d0c02e654eed9da7d74174de49d5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49462.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49462
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
