# [H] RDMA/core: Fix ib block iterator counter overflow

## Summary
Severity: High
Advisory: CVE-2023-53026
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-53026
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/core: Fix ib block iterator counter overflow

When registering a new DMA MR after selecting the best aligned page size
for it, we iterate over the given sglist to split each entry to smaller,
aligned to the selected page size, DMA blocks.

In given circumstances where the sg entry and page size fit certain
sizes and the sg entry is not aligned to the selected page size, the
total size of the aligned pages we need to cover the sg entry is >= 4GB.
Under this circumstances, while iterating page aligned blocks, the
counter responsible for counting how much we advanced from the start of
the sg entry is overflowed because its type is u32 and we pass 4GB in
size. This can lead to an infinite loop inside the iterator function
because the overflow prevents the counter to be larger
than the size of the sg entry.

Fix the presented problem by changing the advancement condition to
eliminate overflow.

Backtrace:
[  192.374329] efa_reg_user_mr_dmabuf
[  192.376783] efa_register_mr
[  192.382579] pgsz_bitmap 0xfffff000 rounddown 0x80000000
[  192.386423] pg_sz [0x80000000] umem_length[0xc0000000]
[  192.392657] start 0x0 length 0xc0000000 params.page_shift 31 params.page_num 3
[  192.399559] hp_cnt[3], pages_in_hp[524288]
[  192.403690] umem->sgt_append.sgt.nents[1]
[  192.407905] number entries: [1], pg_bit: [31]
[  192.411397] biter->__sg_nents [1] biter->__sg [0000000008b0c5d8]
[  192.415601] biter->__sg_advance [665837568] sg_dma_len[3221225472]
[  192.419823] biter->__sg_nents [1] biter->__sg [0000000008b0c5d8]
[  192.423976] biter->__sg_advance [2813321216] sg_dma_len[3221225472]
[  192.428243] biter->__sg_nents [1] biter->__sg [0000000008b0c5d8]
[  192.432397] biter->__sg_advance [665837568] sg_dma_len[3221225472]

## References
- https://git.kernel.org/stable/c/0afec5e9cea732cb47014655685a2a47fb180c31
- https://git.kernel.org/stable/c/362c9489720b31b6aa7491423ba65a4e98aa9838
- https://git.kernel.org/stable/c/43811d07ea64366af8ec9e168c558ec51440c39e
- https://git.kernel.org/stable/c/902063a9fea5f8252df392ade746bc9cfd07a5ae
- https://git.kernel.org/stable/c/d66c1d4178c219b6e7d7a6f714e3e3656faccc36
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53026.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53026
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
