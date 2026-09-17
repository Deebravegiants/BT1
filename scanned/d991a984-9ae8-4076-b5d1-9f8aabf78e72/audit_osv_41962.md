# [H] mm: fix __vm_normal_page() to handle missing support for pmd_special()/pud_special()

## Summary
Severity: High
Advisory: CVE-2026-64181
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64181
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: fix __vm_normal_page() to handle missing support for pmd_special()/pud_special()

On x86 32-bit with THP enabled, zap_huge_pmd() is seen to generate a
"WARNING: mm/memory.c:735 at __vm_normal_page+0x6a/0x7d", from the
VM_WARN_ON_ONCE(is_zero_pfn(pfn) || is_huge_zero_pfn(pfn)); followed by
"BUG: Bad rss-counter state"s, then later "BUG: Bad page state"s when
reclaim gets to call shrink_huge_zero_folio_scan().

It's as if the _PAGE_SPECIAL bit never got set in the huge_zero pmd: and
indeed, whereas pte_special() and pte_mkspecial() are subject to a
dedicated CONFIG_ARCH_HAS_PTE_SPECIAL, pmd_special() and pmd_mkspecial()
are subject to CONFIG_ARCH_SUPPORTS_PMD_PFNMAP, which is never enabled on
any 32-bit architecture.

While the problem was exposed through commit d80a9cb1a64a
("mm/huge_memory: add and use normal_or_softleaf_folio_pmd()"), it was an
oversight in commit af38538801c6 ("mm/memory: factor out common code from
vm_normal_page_*()") and would result in other problems:
* huge zero folio accounted in smaps, pagemap (PAGE_IS_FILE) and
  numamaps as file-backed THP
* folio_walk_start() returning the folio even without FW_ZEROPAGE set.
  Callers seem to tolerate that, though.

... and triggering the VM_WARN_ON_ONE(), although never reported so far.

To fix it, teach vm_normal_page_pmd()/vm_normal_page_pud() to consider
whether pmd_special/pud_special is actually implemented.

## References
- https://git.kernel.org/stable/c/62153767e8fc3889bc6508e9ffe927aaf64c4334
- https://git.kernel.org/stable/c/9052ea2ee2233be5d4786b8909151ca2bfbedf99
- https://git.kernel.org/stable/c/c0c6ccd9828c3a1950623b546fa57292a77b5c73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64181.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64181
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
