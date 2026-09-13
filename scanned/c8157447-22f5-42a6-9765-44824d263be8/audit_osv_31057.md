# [M] mm/page_alloc: don't call pfn_to_page() on possibly non-existent PFN in split_large_buddy()

## Summary
Severity: Medium
Advisory: CVE-2024-57881
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-57881
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/page_alloc: don't call pfn_to_page() on possibly non-existent PFN in split_large_buddy()

In split_large_buddy(), we might call pfn_to_page() on a PFN that might
not exist.  In corner cases, such as when freeing the highest pageblock in
the last memory section, this could result with CONFIG_SPARSEMEM &&
!CONFIG_SPARSEMEM_EXTREME in __pfn_to_section() returning NULL and and
__section_mem_map_addr() dereferencing that NULL pointer.

Let's fix it, and avoid doing a pfn_to_page() call for the first
iteration, where we already have the page.

So far this was found by code inspection, but let's just CC stable as the
fix is easy.

## References
- https://git.kernel.org/stable/c/4234ca9884bcae9e48ed38652d91696ad5cd591d
- https://git.kernel.org/stable/c/faeec8e23c10bd30e8aa759a2eb3018dae00f924
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
