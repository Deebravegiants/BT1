# [H] spi: imx: reconfigure for PIO when DMA cannot be started

## Summary
Severity: High
Advisory: CVE-2026-72134
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72134
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: imx: reconfigure for PIO when DMA cannot be started

When spi_imx_can_dma() selects DMA, the ECSPI is configured for DMA:
spi_imx_setupxfer() sets CTRL.SMC and clears dynamic_burst, and
spi_imx_dma_transfer() programs the dynamic-burst BURST_LENGTH and the
SDMA watermarks.

If the DMA descriptor cannot be prepared (dmaengine_prep_slave_single()
returns NULL), the transfer is failed with SPI_TRANS_FAIL_NO_START and
falls back to PIO. The dynamic-burst DMA path uses its own bounce
buffers instead of the SPI core's mapping, so xfer->{tx,rx}_sg_mapped
are not set and the core's DMA->PIO retry is skipped; the driver falls
back to PIO internally. But none of the DMA-mode configuration is
undone, so the PIO transfer runs with CTRL.SMC set, the wrong burst
length and dynamic_burst cleared, and the transferred data is corrupted.

This is easily hit on i.MX8MP boards that describe ECSPI DMA in the
device tree but run SDMA on ROM firmware (no external sdma-imx7d.bin):
every ECSPI DMA prepare fails. An Infineon SLB9670 TPM on ECSPI1 then
returns shifted TPM2_GetCapability data, is flagged "field failure
mode", /dev/tpmrm0 is never created.

Set controller->fallback before re-running spi_imx_setupxfer() so the
ECSPI is reconfigured exactly like a normal PIO transfer. With
controller->fallback set, spi_imx_setupxfer() sees spi_imx_can_dma()
return false, so it clears spi_imx->usedma and reprograms the controller
(clears CTRL.SMC, restores dynamic_burst and the PIO burst length). No
explicit spi_imx->usedma = false is needed: setupxfer() already updates
it from the can_dma() result.

## References
- https://git.kernel.org/stable/c/245404c26563aafb36aafb01298f148db1851be3
- https://git.kernel.org/stable/c/40dee2d3e9994aed9efe7bed40eb0e4d38d5a25c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72134.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72134
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
