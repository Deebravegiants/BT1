# [M] dmaengine: imx-sdma: Fix a possible memory leak in sdma_transfer_init

## Summary
Severity: Medium
Advisory: CVE-2022-49746
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49746
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.167, >=5.11.0 <5.15.92, >=5.16.0 <6.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: imx-sdma: Fix a possible memory leak in sdma_transfer_init

If the function sdma_load_context() fails, the sdma_desc will be
freed, but the allocated desc->bd is forgot to be freed.

We already met the sdma_load_context() failure case and the log as
below:
[ 450.699064] imx-sdma 30bd0000.dma-controller: Timeout waiting for CH0 ready
...

In this case, the desc->bd will not be freed without this change.

## References
- https://git.kernel.org/stable/c/1417f59ac0b02130ee56c0c50794b9b257be3d17
- https://git.kernel.org/stable/c/43acd767bd90c5d4172ce7fee5d9007a9a08dea9
- https://git.kernel.org/stable/c/80ee99e52936b2c04cc37b17a14b2ae2f9d282ac
- https://git.kernel.org/stable/c/bd0050b7ffa87c7b260d563646af612f4112a778
- https://git.kernel.org/stable/c/ce4745a6b8016fae74c95dcd457d4ceef7d98af1
- https://git.kernel.org/stable/c/dbe634ce824329d8f14079c3e9f8f11670894bec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49746.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49746
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
