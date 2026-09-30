# [M] soc: rockchip: Fix refcount leak in rockchip_grf_init

## Summary
Severity: Medium
Advisory: CVE-2022-49382
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49382
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.122, >=5.11.0 <5.15.47, >=5.16.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

soc: rockchip: Fix refcount leak in rockchip_grf_init

of_find_matching_node_and_match returns a node pointer with refcount
incremented, we should use of_node_put() on it when done.
Add missing of_node_put() to avoid refcount leak.

## References
- https://git.kernel.org/stable/c/042571fe1d171773655ad706715ecc865913d9a4
- https://git.kernel.org/stable/c/28133325526b92921f3269fdf97a20d90b92b217
- https://git.kernel.org/stable/c/5b3e990f85eb034faa461e691e719e8ce9e2a3c8
- https://git.kernel.org/stable/c/69a30b2ed620c2206cbbd1e9c112e4fc584e02bd
- https://git.kernel.org/stable/c/8f64e84924604bb969ee1fbc4b8d7d09b9214889
- https://git.kernel.org/stable/c/9b59588d8be91c96bfb0371e912ceb4f16315dbf
- https://git.kernel.org/stable/c/aab25b669cb9fd3698c2631be4435f4fe92d9e59
- https://git.kernel.org/stable/c/d5422f323858cad3ac3581075f9a3a5e0d41c0d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49382.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49382
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
