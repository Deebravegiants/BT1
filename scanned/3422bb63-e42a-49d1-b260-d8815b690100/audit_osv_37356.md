# [H] mm/huge_memory: fix use of NULL folio in move_pages_huge_pmd()

## Summary
Severity: High
Advisory: CVE-2026-31397
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31397
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/huge_memory: fix use of NULL folio in move_pages_huge_pmd()

move_pages_huge_pmd() handles UFFDIO_MOVE for both normal THPs and huge
zero pages.  For the huge zero page path, src_folio is explicitly set to
NULL, and is used as a sentinel to skip folio operations like lock and
rmap.

In the huge zero page branch, src_folio is NULL, so folio_mk_pmd(NULL,
pgprot) passes NULL through folio_pfn() and page_to_pfn().  With
SPARSEMEM_VMEMMAP this silently produces a bogus PFN, installing a PMD
pointing to non-existent physical memory.  On other memory models it is a
NULL dereference.

Use page_folio(src_page) to obtain the valid huge zero folio from the
page, which was obtained from pmd_page() and remains valid throughout.

After commit d82d09e48219 ("mm/huge_memory: mark PMD mappings of the huge
zero folio special"), moved huge zero PMDs must remain special so
vm_normal_page_pmd() continues to treat them as special mappings.

move_pages_huge_pmd() currently reconstructs the destination PMD in the
huge zero page branch, which drops PMD state such as pmd_special() on
architectures with CONFIG_ARCH_HAS_PTE_SPECIAL.  As a result,
vm_normal_page_pmd() can treat the moved huge zero PMD as a normal page
and corrupt its refcount.

Instead of reconstructing the PMD from the folio, derive the destination
entry from src_pmdval after pmdp_huge_clear_flush(), then handle the PMD
metadata the same way move_huge_pmd() does for moved entries by marking it
soft-dirty and clearing uffd-wp.

## References
- https://git.kernel.org/stable/c/e3133d0986dc5a231d5419167dbac65312b28b41
- https://git.kernel.org/stable/c/f3caaee0f9e489fd2282d4ce45791dc8aed2da62
- https://git.kernel.org/stable/c/fae654083bfa409bb2244f390232e2be47f05bfc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31397.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31397
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
