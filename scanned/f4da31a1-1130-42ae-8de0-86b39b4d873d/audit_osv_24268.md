# [H] nvme-pci: fix mempool alloc size

## Summary
Severity: High
Advisory: CVE-2022-50756
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50756
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.17, >=6.1.0 <6.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvme-pci: fix mempool alloc size

Convert the max size to bytes to match the units of the divisor that
calculates the worst-case number of PRP entries.

The result is used to determine how many PRP Lists are required. The
code was previously rounding this to 1 list, but we can require 2 in the
worst case. In that scenario, the driver would corrupt memory beyond the
size provided by the mempool.

While unlikely to occur (you'd need a 4MB in exactly 127 phys segments
on a queue that doesn't support SGLs), this memory corruption has been
observed by kfence.

## References
- https://git.kernel.org/stable/c/9141144b37f30e3e7fa024bcfa0a13011e546ba9
- https://git.kernel.org/stable/c/b1814724e0d7162bdf4799f2d565381bc2251c63
- https://git.kernel.org/stable/c/c89a529e823d51dd23c7ec0c047c7a454a428541
- https://git.kernel.org/stable/c/dfb6d54893d544151e7f480bc44cfe7823f5ad23
- https://git.kernel.org/stable/c/e1777b4286e526c58b4ee699344b0ad85aaf83a0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50756.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50756
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
