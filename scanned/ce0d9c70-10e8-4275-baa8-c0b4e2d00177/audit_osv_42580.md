# [H] mtd: rawnand: lpc32xx_slc: fail DMA transfer on completion timeout

## Summary
Severity: High
Advisory: CVE-2026-68466
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68466
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mtd: rawnand: lpc32xx_slc: fail DMA transfer on completion timeout

lpc32xx_xmit_dma() waits for the DMA completion callback but ignores
wait_for_completion_timeout(). A timed out DMA transfer is therefore
unmapped and reported as successful to the NAND read/write path.

Return -ETIMEDOUT when the completion wait expires. Terminate the DMA
channel before unmapping the scatterlist so the timed out transfer cannot
continue to access the buffer after the error is returned.

## References
- https://git.kernel.org/stable/c/17a8ce84964f243c8f89dc7353ac7e8d3137bc74
- https://git.kernel.org/stable/c/307e4f4c1d4e1575b3495ecc6e41aa2adc40f491
- https://git.kernel.org/stable/c/623c4d8e740debb4af28981e3d4e209f9d0260a4
- https://git.kernel.org/stable/c/8f5c3ee53a5dc1a0f7cfd780485f2c8b5d17f91d
- https://git.kernel.org/stable/c/bd4a622786f92e1f183f7557ab89dd32891cef60
- https://git.kernel.org/stable/c/c367af37ce7238c96c6071337149099467160746
- https://git.kernel.org/stable/c/cb2031f8b226efbd13735c07b075e5f14ec11f6d
- https://git.kernel.org/stable/c/cf7258f57d18026b8f77c0e80ff1805e9caf7250
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68466.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68466
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
