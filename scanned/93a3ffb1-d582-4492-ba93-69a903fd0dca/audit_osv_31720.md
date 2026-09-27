# [H] net: fec: handle page_pool_dev_alloc_pages error

## Summary
Severity: High
Advisory: CVE-2025-21676
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-31
Source: https://osv.dev/vulnerability/CVE-2025-21676
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.1.0 <6.1.167, >=6.2.0 <6.6.74, >=6.7.0 <6.12.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fec: handle page_pool_dev_alloc_pages error

The fec_enet_update_cbd function calls page_pool_dev_alloc_pages but did
not handle the case when it returned NULL. There was a WARN_ON(!new_page)
but it would still proceed to use the NULL pointer and then crash.

This case does seem somewhat rare but when the system is under memory
pressure it can happen. One case where I can duplicate this with some
frequency is when writing over a smbd share to a SATA HDD attached to an
imx6q.

Setting /proc/sys/vm/min_free_kbytes to higher values also seems to solve
the problem for my test case. But it still seems wrong that the fec driver
ignores the memory allocation error and can crash.

This commit handles the allocation error by dropping the current packet.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/001ba0902046cb6c352494df610718c0763e77a5
- https://git.kernel.org/stable/c/1425cb829556398f594658512d49292f988a2ab0
- https://git.kernel.org/stable/c/8a0097db0544b658c159ac787319737712063a23
- https://git.kernel.org/stable/c/eacdcc14f3c8d4c1447565521e792ddb3a67e08d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21676.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
