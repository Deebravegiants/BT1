# [H] mm/migrate: fix shmem xarray update during migration

## Summary
Severity: High
Advisory: CVE-2025-22015
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/CVE-2025-22015
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.132, >=6.2.0 <6.6.85, >=6.7.0 <6.13.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/migrate: fix shmem xarray update during migration

A shmem folio can be either in page cache or in swap cache, but not at the
same time.  Namely, once it is in swap cache, folio->mapping should be
NULL, and the folio is no longer in a shmem mapping.

In __folio_migrate_mapping(), to determine the number of xarray entries to
update, folio_test_swapbacked() is used, but that conflates shmem in page
cache case and shmem in swap cache case.  It leads to xarray multi-index
entry corruption, since it turns a sibling entry to a normal entry during
xas_store() (see [1] for a userspace reproduction).  Fix it by only using
folio_test_swapcache() to determine whether xarray is storing swap cache
entries or not to choose the right number of xarray entries to update.

[1] https://lore.kernel.org/linux-mm/Z8idPCkaJW1IChjT@casper.infradead.org/

Note:
In __split_huge_page(), folio_test_anon() && folio_test_swapcache() is
used to get swap_cache address space, but that ignores the shmem folio in
swap cache case.  It could lead to NULL pointer dereferencing when a
in-swap-cache shmem folio is split at __xa_store(), since
!folio_test_anon() is true and folio->mapping is NULL.  But fortunately,
its caller split_huge_page_to_list_to_order() bails out early with EBUSY
when folio->mapping is NULL.  So no need to take care of it here.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/29124ae980e2860f0eec7355949d3d3292ee81da
- https://git.kernel.org/stable/c/49100c0b070e900f87c8fac3be9b9ef8a30fa673
- https://git.kernel.org/stable/c/60cf233b585cdf1f3c5e52d1225606b86acd08b0
- https://git.kernel.org/stable/c/75cfb92eb63298d717b6b0118f91ba12c4fcfeb5
- https://git.kernel.org/stable/c/c057ee03f751d6cecf7ee64f52f6545d94082aaa
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22015.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22015
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
