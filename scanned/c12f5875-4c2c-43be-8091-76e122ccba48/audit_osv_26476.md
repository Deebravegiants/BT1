# [H] cacheinfo: Fix shared_cpu_map to handle shared caches at different levels

## Summary
Severity: High
Advisory: CVE-2023-53254
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2023-53254
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.19.0 <6.1.18, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

cacheinfo: Fix shared_cpu_map to handle shared caches at different levels

The cacheinfo sets up the shared_cpu_map by checking whether the caches
with the same index are shared between CPUs. However, this will trigger
slab-out-of-bounds access if the CPUs do not have the same cache hierarchy.
Another problem is the mismatched shared_cpu_map when the shared cache does
not have the same index between CPUs.

CPU0	I	D	L3
index	0	1	2	x
	^	^	^	^
index	0	1	2	3
CPU1	I	D	L2	L3

This patch checks each cache is shared with all caches on other CPUs.

## References
- https://git.kernel.org/stable/c/198102c9103fc78d8478495971947af77edb05c1
- https://git.kernel.org/stable/c/2f588d0345d69a35e451077afed428fd057a5e34
- https://git.kernel.org/stable/c/dea49f2993f57d8a2df2cacb0bf649ef49b28879
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53254.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53254
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
