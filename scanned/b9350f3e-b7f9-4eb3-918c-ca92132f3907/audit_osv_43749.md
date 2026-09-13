# [H] mm: fix incorrect flush address in direct page table reclaim

## Summary
Severity: High
Advisory: CVE-2026-74674
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74674
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.0.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm: fix incorrect flush address in direct page table reclaim

When zap_pte_range reclaims a page table, it does:

    pte_free_tlb(tlb, pmd_pgtable(pmdval), addr);

and this is unconditionally wrong: if this code executes, addr *always*
points one past the end of the range covered by the table.  The addr
parameter is used to flush the TLB (really the paging-structure-cache)
to drop references to the to-be-freed table, and any architecture that
cares about the parameter will flush the wrong address.  (But they'll
still free the correct page).

I think it's worth contemplating why the kernel works at all.

If we hit the offending line of code, we will first clear the PMD entry
(line 1954, zap_empty_pte_table), then we will issue pending flushes if
force_flush is set (tlb_flush_mmu_tlbonly(tlb)), then we will skip the
retry on line 1979 (phew!), and then we will do the offending
pte_free_tlb call.  *Or* we will clear the PMD entry immediately before
pte_free_tlb (line 1983, zap_pte_table_if_empty).

If we have any pending flushes (i.e. we actually zapped any last-level
entries) at the time we clear the PMD entry, then the flush really ought
to flush all references to the table (Linus certainly seems to think it
will on all architectures [0]).

The condition under which we have no accumulated flushes at the time of
the clear is very complex (the whole zap_pte_range function has absurdly
complex control flow).  If we do hit the bad case, then we will end up
clearing the PMD entry after the last time the range is flushed, and any
CPU is free to cache a reference to the (empty) page table.  If this
happens due to an ordinary read or write, it would segfault, so it would
be rare.  But the cache could be speculatively filled as well.  Then
we'll flush the wrong address and then free and possibly reuse the
table.

On x86, even flushing the wrong address works on non-KPTI Intel systems
because INVLPG flushes *all* paging-structure-caches, not just the ones
for the target address.  But INVPCID does not, and flush_tlb_one_user
will use INVPCID if it's available.  And then we're toast.  AMD systems
are more susceptible: we set the EFER.TCE bit, which makes even INVLPG
only flush the target address.

I think this might fix an issue in ripgrep reported here:
https://github.com/BurntSushi/ripgrep/issues/3494

[0] https://lore.kernel.org/all/CA+55aFzBggoXtNXQeng5d_mRoDnaMBE5Y+URs+PHR67nUpMtaw@mail.gmail.com/T/#u

## References
- https://git.kernel.org/stable/c/0b8ff21cbda8808c86b18f1b0ca2d0025af9a80a
- https://git.kernel.org/stable/c/478a1c3abebfc717db0d1281a9cdd7befafee542
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74674.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74674
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
