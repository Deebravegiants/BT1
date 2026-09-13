# [H] spi: rockchip-sfc: Fix DMA-API usage

## Summary
Severity: High
Advisory: CVE-2025-40356
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-40356
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.14.0 <6.17.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: rockchip-sfc: Fix DMA-API usage

Use DMA-API dma_map_single() call for getting the DMA address of the
transfer buffer instead of hacking with virt_to_phys().

This fixes the following DMA-API debug warning:
------------[ cut here ]------------
DMA-API: rockchip-sfc fe300000.spi: device driver tries to sync DMA memory it has not allocated [device address=0x000000000cf70000] [size=288 bytes]
WARNING: kernel/dma/debug.c:1106 at check_sync+0x1d8/0x690, CPU#2: systemd-udevd/151
Modules linked in: ...
Hardware name: Hardkernel ODROID-M1 (DT)
pstate: 604000c9 (nZCv daIF +PAN -UAO -TCO -DIT -SSBS BTYPE=--)
pc : check_sync+0x1d8/0x690
lr : check_sync+0x1d8/0x690
..
Call trace:
 check_sync+0x1d8/0x690 (P)
 debug_dma_sync_single_for_cpu+0x84/0x8c
 __dma_sync_single_for_cpu+0x88/0x234
 rockchip_sfc_exec_mem_op+0x4a0/0x798 [spi_rockchip_sfc]
 spi_mem_exec_op+0x408/0x498
 spi_nor_read_data+0x170/0x184
 spi_nor_read_sfdp+0x74/0xe4
 spi_nor_parse_sfdp+0x120/0x11f0
 spi_nor_sfdp_init_params_deprecated+0x3c/0x8c
 spi_nor_scan+0x690/0xf88
 spi_nor_probe+0xe4/0x304
 spi_mem_probe+0x6c/0xa8
 spi_probe+0x94/0xd4
 really_probe+0xbc/0x298
 ...

## References
- https://git.kernel.org/stable/c/22810d4cb0e8a7d51b24527e73beac60afc1c693
- https://git.kernel.org/stable/c/ee795e82e10197c070efd380dc9615c73dffad6c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40356.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40356
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
