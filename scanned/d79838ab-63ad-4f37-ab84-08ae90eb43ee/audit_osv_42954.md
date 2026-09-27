# [H] mm/hugetlb: fix hugetlb cgroup rsvd charge/uncharge mismatch

## Summary
Severity: High
Advisory: CVE-2026-72213
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72213
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/hugetlb: fix hugetlb cgroup rsvd charge/uncharge mismatch

In alloc_hugetlb_folio(), a single h_cg pointer is used for both the rsvd
and non-rsvd hugetlb cgroup charges.  When map_chg is set,
hugetlb_cgroup_charge_cgroup_rsvd() stores the charged cgroup in h_cg, but
the immediately following hugetlb_cgroup_charge_cgroup() overwrites h_cg
with the non-rsvd cgroup pointer.

As a result, hugetlb_cgroup_commit_charge_rsvd() stores the wrong
(non-rsvd) cgroup pointer into the folio's rsvd slot.

When the folio is later freed, free_huge_folio() unconditionally calls
both hugetlb_cgroup_uncharge_folio() and
hugetlb_cgroup_uncharge_folio_rsvd().  The rsvd uncharge reads back the
wrong cgroup from the folio and decrements a counter that was never
charged for that cgroup, causing a page_counter underflow:

  page_counter underflow: -512 nr_pages=512
  WARNING: mm/page_counter.c:61 at page_counter_cancel

Fix this by introducing a separate h_cg_rsvd pointer exclusively for the
rsvd charge path, keeping the rsvd and non-rsvd charges fully independent
through their charge, commit, and error uncharge paths.

## References
- https://git.kernel.org/stable/c/15807d0ddde37407af72859426b654f3d1972b00
- https://git.kernel.org/stable/c/1697d253f51cf5e3825a3423ff49e128a3502ab2
- https://git.kernel.org/stable/c/5c32ae4a91fb5f4941328e0c1720a7fa4189c3bd
- https://git.kernel.org/stable/c/b785f2bd9496facedc0a031be09cddcd1d3c84d3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72213.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72213
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
