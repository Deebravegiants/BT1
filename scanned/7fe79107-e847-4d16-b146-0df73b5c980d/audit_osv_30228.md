# [C] net: ethernet: mtk_eth_soc: fix memory corruption during fq dma init

## Summary
Severity: Critical
Advisory: CVE-2024-50206
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50206
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_eth_soc: fix memory corruption during fq dma init

The loop responsible for allocating up to MTK_FQ_DMA_LENGTH buffers must
only touch as many descriptors, otherwise it ends up corrupting unrelated
memory. Fix the loop iteration count accordingly.

## References
- https://git.kernel.org/stable/c/68cd084e3ec1512cd383cb3e9cf0ab7ab413724c
- https://git.kernel.org/stable/c/88806efc034a9830f483963326b99930ad519af1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50206.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
