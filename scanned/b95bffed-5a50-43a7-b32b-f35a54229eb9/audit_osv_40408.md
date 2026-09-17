# [H] misc: fastrpc: fix DMA address corruption due to find_vma misuse

## Summary
Severity: High
Advisory: CVE-2026-53159
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53159
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.260, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

misc: fastrpc: fix DMA address corruption due to find_vma misuse

fastrpc_get_args() uses find_vma() to look up the VMA for a user-provided
pointer and compute a DMA address offset. When the address falls in a gap
before the returned VMA, (ptr & PAGE_MASK) - vma->vm_start underflows,
corrupting the DMA address sent to the DSP.

Replace find_vma() with vma_lookup(), which returns NULL when the address
is not contained within any VMA.

## References
- https://git.kernel.org/stable/c/2d0f47e27c1fa718b29c69aa7c96a2c5161bc2c2
- https://git.kernel.org/stable/c/464c6ad2aa16e1e1df9d559289199356493d1e00
- https://git.kernel.org/stable/c/53e06f8a3c2b085c31bf1284e2ebcb8036e99625
- https://git.kernel.org/stable/c/708c17b52c60fe7a57e73b495bdee50f58feb48c
- https://git.kernel.org/stable/c/7ba7b30ddb04646d4d638f4d8c4718a304bbbddd
- https://git.kernel.org/stable/c/d3e26df2e8eb361e6bef096b2fd565476a1f14c4
- https://git.kernel.org/stable/c/d43afc412d439ffca1567e7ca8652be22f272b3b
- https://git.kernel.org/stable/c/e69e306a4cccb40a73511350cb280825a556ce3c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53159.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53159
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
