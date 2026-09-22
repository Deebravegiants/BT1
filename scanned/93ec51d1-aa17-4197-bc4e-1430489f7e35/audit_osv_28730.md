# [H] mm: turn folio_test_hugetlb into a PageType

## Summary
Severity: High
Advisory: CVE-2024-35993
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-20
Source: https://osv.dev/vulnerability/CVE-2024-35993
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.30, >=6.7.0 <6.8.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: turn folio_test_hugetlb into a PageType

The current folio_test_hugetlb() can be fooled by a concurrent folio split
into returning true for a folio which has never belonged to hugetlbfs. 
This can't happen if the caller holds a refcount on it, but we have a few
places (memory-failure, compaction, procfs) which do not and should not
take a speculative reference.

Since hugetlb pages do not use individual page mapcounts (they are always
fully mapped and use the entire_mapcount field to record the number of
mappings), the PageType field is available now that page_mapcount()
ignores the value in this field.

In compaction and with CONFIG_DEBUG_VM enabled, the current implementation
can result in an oops, as reported by Luis. This happens since 9c5ccf2db04b
("mm: remove HUGETLB_PAGE_DTOR") effectively added some VM_BUG_ON() checks
in the PageHuge() testing path.

[willy@infradead.org: update vmcoreinfo]

## References
- https://git.kernel.org/stable/c/2431b5f2650dfc47ce782d1ca7b02d6b3916976f
- https://git.kernel.org/stable/c/9fdcc5b6359dfdaa52a55033bf50e2cedd66eb32
- https://git.kernel.org/stable/c/d99e3140a4d33e26066183ff727d8f02f56bec64
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35993.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35993
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
