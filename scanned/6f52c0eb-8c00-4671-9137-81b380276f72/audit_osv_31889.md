# [H] drm/xe/hmm: Don't dereference struct page pointers without notifier lock

## Summary
Severity: High
Advisory: CVE-2025-21939
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21939
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe/hmm: Don't dereference struct page pointers without notifier lock

The pnfs that we obtain from hmm_range_fault() point to pages that
we don't have a reference on, and the guarantee that they are still
in the cpu page-tables is that the notifier lock must be held and the
notifier seqno is still valid.

So while building the sg table and marking the pages accesses / dirty
we need to hold this lock with a validated seqno.

However, the lock is reclaim tainted which makes
sg_alloc_table_from_pages_segment() unusable, since it internally
allocates memory.

Instead build the sg-table manually. For the non-iommu case
this might lead to fewer coalesces, but if that's a problem it can
be fixed up later in the resource cursor code. For the iommu case,
the whole sg-table may still be coalesced to a single contigous
device va region.

This avoids marking pages that we don't own dirty and accessed, and
it also avoid dereferencing struct pages that we don't own.

v2:
- Use assert to check whether hmm pfns are valid (Matthew Auld)
- Take into account that large pages may cross range boundaries
  (Matthew Auld)

v3:
- Don't unnecessarily check for a non-freed sg-table. (Matthew Auld)
- Add a missing up_read() in an error path. (Matthew Auld)

(cherry picked from commit ea3e66d280ce2576664a862693d1da8fd324c317)

## References
- https://git.kernel.org/stable/c/0a98219bcc961edd3388960576e4353e123b4a51
- https://git.kernel.org/stable/c/2a24c98f0e4cc994334598d4f3a851972064809d
- https://git.kernel.org/stable/c/f9326f529da7298a95643c3267f1c0fdb0db55eb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21939.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21939
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
