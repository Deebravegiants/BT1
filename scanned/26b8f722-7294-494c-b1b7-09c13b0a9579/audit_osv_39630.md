# [C] RDMA/rxe: Fix iova-to-va conversion for MR page sizes != PAGE_SIZE

## Summary
Severity: Critical
Advisory: CVE-2026-46325
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46325
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/rxe: Fix iova-to-va conversion for MR page sizes != PAGE_SIZE

The current implementation incorrectly handles memory regions (MRs) with
page sizes different from the system PAGE_SIZE. The core issue is that
rxe_set_page() is called with mr->page_size step increments, but the
page_list stores individual struct page pointers, each representing
PAGE_SIZE of memory.

ib_sg_to_page() has ensured that when i>=1 either
a) SG[i-1].dma_end and SG[i].dma_addr are contiguous
or
b) SG[i-1].dma_end and SG[i].dma_addr are mr->page_size aligned.

This leads to incorrect iova-to-va conversion in scenarios:

1) page_size < PAGE_SIZE (e.g., MR: 4K, system: 64K):
   ibmr->iova = 0x181800
   sg[0]: dma_addr=0x181800, len=0x800
   sg[1]: dma_addr=0x173000, len=0x1000

   Access iova = 0x181800 + 0x810 = 0x182010
   Expected VA: 0x173010 (second SG, offset 0x10)
   Before fix:
     - index = (0x182010 >> 12) - (0x181800 >> 12) = 1
     - page_offset = 0x182010 & 0xFFF = 0x10
     - xarray[1] stores system page base 0x170000
     - Resulting VA: 0x170000 + 0x10 = 0x170010 (wrong)

2) page_size > PAGE_SIZE (e.g., MR: 64K, system: 4K):
   ibmr->iova = 0x18f800
   sg[0]: dma_addr=0x18f800, len=0x800
   sg[1]: dma_addr=0x170000, len=0x1000

   Access iova = 0x18f800 + 0x810 = 0x190010
   Expected VA: 0x170010 (second SG, offset 0x10)
   Before fix:
     - index = (0x190010 >> 16) - (0x18f800 >> 16) = 1
     - page_offset = 0x190010 & 0xFFFF = 0x10
     - xarray[1] stores system page for dma_addr 0x170000
     - Resulting VA: system page of 0x170000 + 0x10 = 0x170010 (wrong)

Yi Zhang reported a kernel panic[1] years ago related to this defect.

Solution:
1. Replace xarray with pre-allocated rxe_mr_page array for sequential
   indexing (all MR page indices are contiguous)
2. Each rxe_mr_page stores both struct page* and offset within the
   system page
3. Handle MR page_size != PAGE_SIZE relationships:
   - page_size > PAGE_SIZE: Split MR pages into multiple system pages
   - page_size <= PAGE_SIZE: Store offset within system page
4. Add boundary checks and compatibility validation

This ensures correct iova-to-va conversion regardless of MR page size
and system PAGE_SIZE relationship, while improving performance through
array-based sequential access.

Tests on 4K and 64K PAGE_SIZE hosts:
- rdma-core/pytests
  $ ./build/bin/run_tests.py  --dev eth0_rxe
- blktest:
  $ TIMEOUT=30 QUICK_RUN=1 USE_RXE=1 NVMET_TRTYPES=rdma ./check nvme srp rnbd

[1] https://lore.kernel.org/all/CAHj4cs9XRqE25jyVw9rj9YugffLn5+f=1znaBEnu1usLOciD+g@mail.gmail.com/T/

## References
- https://git.kernel.org/stable/c/12985e5915a0b8354796efadaaeb201eed115377
- https://git.kernel.org/stable/c/409c2c5508f3d30627bea576f8676de523cb906e
- https://git.kernel.org/stable/c/836f6c13c9674027793f720be3f15ecd2b90b6ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46325.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46325
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
