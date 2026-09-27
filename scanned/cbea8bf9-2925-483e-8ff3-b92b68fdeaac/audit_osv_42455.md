# [H] arm64: make huge_ptep_get handled unaligned addresses

## Summary
Severity: High
Advisory: CVE-2026-68172
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68172
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: make huge_ptep_get handled unaligned addresses

huge_ptep_get() can be handed a virtual address pointing to the middle
of a contpmd/contpte mapped hugetlb folio (examples of callers are
pagemap_hugetlb_range, page_mapped_in_vma).

The arm64 helper rewalks the pgtables in find_num_contig to answer
whether the huge pte we have maps a contpmd or a contpte hugetlb folio,
and returns CONT_PMDS or CONT_PTES, so that it can collect a/d bits over
the contiguous ptes. We can falsely return CONT_PTES instead of
CONT_PMDS if the addr is not aligned. On systems where CONT_PTES !=
CONT_PMDS (meaning page size is 16K), we could collect excess A/D bit
state, meaning extra work for the kernel. Even worse, we may iterate
beyond the PTE table and dereference a garbage ptep pointer to access
physical memory we don't own. Since the ptep pointer is a linear map
address, we may run off the end of the linear map or into a hole,
dereference a VA not mapped into the kernel pgtables and cause kernel
panic.

Fix this by aligning the pmdp pointer down to a contpmd base before
checking equality with the passed huge pte pointer, to correctly answer
whether the huge pte is the base of a contpmd block.

## References
- https://git.kernel.org/stable/c/9cd4b1a52eff330798d668c1775f8bc450776280
- https://git.kernel.org/stable/c/f3530aec26563f4d483ff31402392961362e9bc6
- https://git.kernel.org/stable/c/f73a8edc2ccc6ec72c37d5c578e7592d2e1f9922
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68172.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68172
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
