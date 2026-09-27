# [H] mm: userfaultfd: fix race of userfaultfd_move and swap cache

## Summary
Severity: High
Advisory: CVE-2025-38242
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38242
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.37, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: userfaultfd: fix race of userfaultfd_move and swap cache

This commit fixes two kinds of races, they may have different results:

Barry reported a BUG_ON in commit c50f8e6053b0, we may see the same
BUG_ON if the filemap lookup returned NULL and folio is added to swap
cache after that.

If another kind of race is triggered (folio changed after lookup) we
may see RSS counter is corrupted:

[  406.893936] BUG: Bad rss-counter state mm:ffff0000c5a9ddc0
type:MM_ANONPAGES val:-1
[  406.894071] BUG: Bad rss-counter state mm:ffff0000c5a9ddc0
type:MM_SHMEMPAGES val:1

Because the folio is being accounted to the wrong VMA.

I'm not sure if there will be any data corruption though, seems no. 
The issues above are critical already.


On seeing a swap entry PTE, userfaultfd_move does a lockless swap cache
lookup, and tries to move the found folio to the faulting vma.  Currently,
it relies on checking the PTE value to ensure that the moved folio still
belongs to the src swap entry and that no new folio has been added to the
swap cache, which turns out to be unreliable.

While working and reviewing the swap table series with Barry, following
existing races are observed and reproduced [1]:

In the example below, move_pages_pte is moving src_pte to dst_pte, where
src_pte is a swap entry PTE holding swap entry S1, and S1 is not in the
swap cache:

CPU1                               CPU2
userfaultfd_move
  move_pages_pte()
    entry = pte_to_swp_entry(orig_src_pte);
    // Here it got entry = S1
    ... < interrupted> ...
                                   <swapin src_pte, alloc and use folio A>
                                   // folio A is a new allocated folio
                                   // and get installed into src_pte
                                   <frees swap entry S1>
                                   // src_pte now points to folio A, S1
                                   // has swap count == 0, it can be freed
                                   // by folio_swap_swap or swap
                                   // allocator's reclaim.
                                   <try to swap out another folio B>
                                   // folio B is a folio in another VMA.
                                   <put folio B to swap cache using S1 >
                                   // S1 is freed, folio B can use it
                                   // for swap out with no problem.
                                   ...
    folio = filemap_get_folio(S1)
    // Got folio B here !!!
    ... < interrupted again> ...
                                   <swapin folio B and free S1>
                                   // Now S1 is free to be used again.
                                   <swapout src_pte & folio A using S1>
                                   // Now src_pte is a swap entry PTE
                                   // holding S1 again.
    folio_trylock(folio)
    move_swap_pte
      double_pt_lock
      is_pte_pages_stable
      // Check passed because src_pte == S1
      folio_move_anon_rmap(...)
      // Moved invalid folio B here !!!

The race window is very short and requires multiple collisions of multiple
rare events, so it's very unlikely to happen, but with a deliberately
constructed reproducer and increased time window, it can be reproduced
easily.

This can be fixed by checking if the folio returned by filemap is the
valid swap cache folio after acquiring the folio lock.

Another similar race is possible: filemap_get_folio may return NULL, but
folio (A) could be swapped in and then swapped out again using the same
swap entry after the lookup.  In such a case, folio (A) may remain in the
swap cache, so it must be moved too:

CPU1                               CPU2
userfaultfd_move
  move_pages_pte()
    entry = pte_to_swp_entry(orig_src_pte);
    // Here it got entry = S1, and S1 is not in swap cache
    folio = filemap_get
---truncated---

## References
- https://git.kernel.org/stable/c/0ea148a799198518d8ebab63ddd0bb6114a103bc
- https://git.kernel.org/stable/c/4c443046d8c9ed8724a4f4c3c2457d3ac8814b2f
- https://git.kernel.org/stable/c/db2ca8074955ca64187a4fb596dd290b9c446cd3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38242.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38242
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
