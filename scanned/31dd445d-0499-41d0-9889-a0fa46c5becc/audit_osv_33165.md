# [M] net/mlx5: HWS, Fix memory leak in hws_pool_buddy_init error path

## Summary
Severity: Medium
Advisory: CVE-2025-39830
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2025-39830
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.16.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/mlx5: HWS, Fix memory leak in hws_pool_buddy_init error path

In the error path of hws_pool_buddy_init(), the buddy allocator cleanup
doesn't free the allocator structure itself, causing a memory leak.

Add the missing kfree() to properly release all allocated memory.

## References
- https://git.kernel.org/stable/c/2c0a959bebdc1ada13cf9a8242f177c5400299e6
- https://git.kernel.org/stable/c/86d13a6f49cb68aa91bd718b1b627e72e77285c1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39830.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39830
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
