# [M] CVE-2021-47047

## Summary
Severity: Medium
Advisory: CVE-2021-47047
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47047
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-zynqmp-gqspi: return -ENOMEM if dma_map_single fails

The spi controller supports 44-bit address space on AXI in DMA mode,
so set dma_addr_t width to 44-bit to avoid using a swiotlb mapping.
In addition, if dma_map_single fails, it should return immediately
instead of continuing doing the DMA operation which bases on invalid
address.

This fixes the following crash which occurs in reading a big block
from flash:

[  123.633577] zynqmp-qspi ff0f0000.spi: swiotlb buffer is full (sz: 4194304 bytes), total 32768 (slots), used 0 (slots)
[  123.644230] zynqmp-qspi ff0f0000.spi: ERR:rxdma:memory not mapped
[  123.784625] Unable to handle kernel paging request at virtual address 00000000003fffc0
[  123.792536] Mem abort info:
[  123.795313]   ESR = 0x96000145
[  123.798351]   EC = 0x25: DABT (current EL), IL = 32 bits
[  123.803655]   SET = 0, FnV = 0
[  123.806693]   EA = 0, S1PTW = 0
[  123.809818] Data abort info:
[  123.812683]   ISV = 0, ISS = 0x00000145
[  123.816503]   CM = 1, WnR = 1
[  123.819455] user pgtable: 4k pages, 48-bit VAs, pgdp=0000000805047000
[  123.825887] [00000000003fffc0] pgd=0000000803b45003, p4d=0000000803b45003, pud=0000000000000000
[  123.834586] Internal error: Oops: 96000145 [#1] PREEMPT SMP

## References
- https://git.kernel.org/stable/c/126bdb606fd2802454e6048caef1be3e25dd121e
- https://git.kernel.org/stable/c/5980a3b9c933408bc22b0e349b78c3ebd7cbf880
- https://git.kernel.org/stable/c/bad5a23cf2b477fa78b85fd392736dae09a1e818
- https://git.kernel.org/stable/c/c26c026eb496261dbc0adbf606cc81989cd2038c
