# [H] mm/page_vma_mapped: fix device-private PMD handling

## Summary
Severity: High
Advisory: CVE-2026-68163
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68163
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/page_vma_mapped: fix device-private PMD handling

Commit 65edfda6f3f2 ("mm/rmap: extend rmap and migration support
device-private entries") introduced the concept of device-private PMD
entries, but did not correctly update the rmap walk code to account for
them.

As a result, when page_vma_mapped_walk() encounters device-private PMD
entries, it takes no action other than to acquire the PMD lock and exit.

However this is highly problematic for two reasons - firstly, device
private entries possess a PFN so check_pmd() needs to be called to ensure
an overlapping PFN range.

Secondly, and more importantly, if PVMW_MIGRATION is set the caller
assumes the returned entry is a migration entry, resulting in memory
corruption when the caller tries to interpret the device private entry as
such.

In addition, commit 146287290023 ("mm/huge_memory: implement
device-private THP splitting") allowed device private PMDs to be split
like THP mappings, but again did not update this code path.

As a result, we might race a PMD split prior to acquiring the PMD lock.

This patch addresses all of these issues by invoking check_pmd(), ensuring
PMVW_MIGRATION is not set and checks whether a split raced us we do for
PMD THP and migration entries.

Instead of checking for a subset of the cases after taking the pmd_lock(),
put device-private along with pmd_trans_huge() and
pmd_is_migration_entry().  Also remove thp_migration_supported() as it is
already guarded by pmd_is_migration_entry().

[akpm@linux-foundation.org: fix Raspberry Pi 1 build, per David]

## References
- https://git.kernel.org/stable/c/ab6209f4b48a98ef14d6766acdb62aa9bb32e670
- https://git.kernel.org/stable/c/f84ca9b1888d8fce7dfefe0e750fa971f8797486
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68163.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68163
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
