# [H] mm/shmem, swap: fix race of truncate and swap entry split

## Summary
Severity: High
Advisory: CVE-2026-23161
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2026-02-14
Source: https://osv.dev/vulnerability/CVE-2026-23161
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.69, >=6.13.0 <6.18.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/shmem, swap: fix race of truncate and swap entry split

The helper for shmem swap freeing is not handling the order of swap
entries correctly.  It uses xa_cmpxchg_irq to erase the swap entry, but it
gets the entry order before that using xa_get_order without lock
protection, and it may get an outdated order value if the entry is split
or changed in other ways after the xa_get_order and before the
xa_cmpxchg_irq.

And besides, the order could grow and be larger than expected, and cause
truncation to erase data beyond the end border.  For example, if the
target entry and following entries are swapped in or freed, then a large
folio was added in place and swapped out, using the same entry, the
xa_cmpxchg_irq will still succeed, it's very unlikely to happen though.

To fix that, open code the Xarray cmpxchg and put the order retrieval and
value checking in the same critical section.  Also, ensure the order won't
exceed the end border, skip it if the entry goes across the border.

Skipping large swap entries crosses the end border is safe here.  Shmem
truncate iterates the range twice, in the first iteration,
find_lock_entries already filtered such entries, and shmem will swapin the
entries that cross the end border and partially truncate the folio (split
the folio or at least zero part of it).  So in the second loop here, if we
see a swap entry that crosses the end order, it must at least have its
content erased already.

I observed random swapoff hangs and kernel panics when stress testing
ZSWAP with shmem.  After applying this patch, all problems are gone.

## References
- https://git.kernel.org/stable/c/8a1968bd997f45a9b11aefeabdd1232e1b6c7184
- https://git.kernel.org/stable/c/a99f9a4669a04662c8f9efe0e62cafc598153139
- https://git.kernel.org/stable/c/b23bee8cdb7aabce5701a7f57414db5a354ae8ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23161.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23161
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
