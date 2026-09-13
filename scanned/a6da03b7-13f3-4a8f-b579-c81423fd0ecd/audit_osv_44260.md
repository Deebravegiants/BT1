# [H] mm/util: don't read __page_2 for order-1 folios in snapshot_page()

## Summary
Severity: High
Advisory: CVE-2026-80685
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80685
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/util: don't read __page_2 for order-1 folios in snapshot_page()

snapshot_page() currently reads __page_2 after checking nr_pages > 1, but
it should only do so when nr_pages > 2.

If an order-1 folio is allocated at the end of a vmemmap section,
__page_2 will not exist and reading it will cause a fault.

During DLPAR memory remove on a 22 TB ppc64le LPAR, snapshot_page() oopsed
on the page isolation path while reading an order-1 folio's __page_2 from
an adjacent absent section (unmapped vmemmap).

Fix this to avoid reading memmap that doesn't exist (e.g., a vmemmap
hole).

## References
- https://git.kernel.org/stable/c/7441d6348c70738e9ed307510db171c7a9b3f4bf
- https://git.kernel.org/stable/c/9668ffe0e2a5e2399dce281620198a2e415871fc
- https://git.kernel.org/stable/c/c649324571206a30949765320b91ccdb4c1722dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80685.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80685
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
