# [H] mm/rmap: initialize nr_pages to 1 at loop start in try_to_unmap_one

## Summary
Severity: High
Advisory: CVE-2026-63950
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63950
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/rmap: initialize nr_pages to 1 at loop start in try_to_unmap_one

Initialize nr_pages to 1 at the start of each loop iteration, like
folio_referenced_one() does.

Without this, nr_pages computed by a previous folio_unmap_pte_batch() call
can be reused on a later iteration that does not run
folio_unmap_pte_batch() again.

mmap a 64K large folio with MAP_ANONYMOUS | MAP_DROPPABLE, then call
madvise(MADV_FREE), then make the last page device-exclusive via
HMM_DMIRROR_EXCLUSIVE.

Trigger node reclaim through sysfs.  Now, in try_to_unmap_one(), we will
first clear the first 15 out of 16 entries mapping the lazyfree folio. 
This will set nr_pages to 15.  In the next pvmw walk, this nr_pages gets
reused on a device-exclusive pte, thus potentially corrupting folio
refcount/mapcount.

At the moment, I have a userspace program which can make the kernel spit
out a trace, but the blow up is in folio_referenced_one(), because there
are existing bugs in the interaction between device-private and rmap
(which too I am investigating).  I did a one liner kernel change to avoid
going into folio_referenced_one(), and the kernel blows up at
folio_remove_rmap_ptes in try_to_unmap_one which is what I wanted.

Note that the bug is there not since file folio batching but lazyfree
folio batching, since device-exclusive only works for anonymous folios.

Userspace visible effect is simply kernel crashing somewhere due to
refcount/mapcount corruption.

## References
- https://git.kernel.org/stable/c/0fcc34d0d8fefca4fea349e45c10e3a3d90350eb
- https://git.kernel.org/stable/c/3f8968e9cbf95d5d87d32218906cab0b9b9eddbe
- https://git.kernel.org/stable/c/f611db9b771b2b6775357555d2517af044fca4f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63950.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63950
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
