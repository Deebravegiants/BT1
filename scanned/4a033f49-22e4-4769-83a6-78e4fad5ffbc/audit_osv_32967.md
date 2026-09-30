# [H] mm/rmap: fix potential out-of-bounds page table access during batched unmap

## Summary
Severity: High
Advisory: CVE-2025-38447
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-25
Source: https://osv.dev/vulnerability/CVE-2025-38447
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/rmap: fix potential out-of-bounds page table access during batched unmap

As pointed out by David[1], the batched unmap logic in
try_to_unmap_one() may read past the end of a PTE table when a large
folio's PTE mappings are not fully contained within a single page
table.

While this scenario might be rare, an issue triggerable from userspace
must be fixed regardless of its likelihood.  This patch fixes the
out-of-bounds access by refactoring the logic into a new helper,
folio_unmap_pte_batch().

The new helper correctly calculates the safe batch size by capping the
scan at both the VMA and PMD boundaries.  To simplify the code, it also
supports partial batching (i.e., any number of pages from 1 up to the
calculated safe maximum), as there is no strong reason to special-case
for fully mapped folios.

## References
- https://git.kernel.org/stable/c/510fe9c15d07e765d96be9a9dc37e5057c6c09f4
- https://git.kernel.org/stable/c/ddd05742b45b083975a0855ef6ebbf88cf1f532a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38447.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38447
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
