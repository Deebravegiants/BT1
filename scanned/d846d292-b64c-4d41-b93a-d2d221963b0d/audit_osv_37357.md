# [H] mm/rmap: fix incorrect pte restoration for lazyfree folios

## Summary
Severity: High
Advisory: CVE-2026-31398
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-31398
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.15.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mm/rmap: fix incorrect pte restoration for lazyfree folios

We batch unmap anonymous lazyfree folios by folio_unmap_pte_batch.  If the
batch has a mix of writable and non-writable bits, we may end up setting
the entire batch writable.  Fix this by respecting writable bit during
batching.

Although on a successful unmap of a lazyfree folio, the soft-dirty bit is
lost, preserve it on pte restoration by respecting the bit during
batching, to make the fix consistent w.r.t both writable bit and
soft-dirty bit.

I was able to write the below reproducer and crash the kernel. 
Explanation of reproducer (set 64K mTHP to always):

Fault in a 64K large folio.  Split the VMA at mid-point with
MADV_DONTFORK.  fork() - parent points to the folio with 8 writable ptes
and 8 non-writable ptes.  Merge the VMAs with MADV_DOFORK so that
folio_unmap_pte_batch() can determine all the 16 ptes as a batch.  Do
MADV_FREE on the range to mark the folio as lazyfree.  Write to the memory
to dirty the pte, eventually rmap will dirty the folio.  Then trigger
reclaim, we will hit the pte restoration path, and the kernel will crash
with the trace given below.

The BUG happens at:

	BUG_ON(atomic_inc_return(&ptc->anon_map_count) > 1 && rw);

The code path is asking for anonymous page to be mapped writable into the
pagetable.  The BUG_ON() firing implies that such a writable page has been
mapped into the pagetables of more than one process, which breaks
anonymous memory/CoW semantics.

[   21.134473] kernel BUG at mm/page_table_check.c:118!
[   21.134497] Internal error: Oops - BUG: 00000000f2000800 [#1]  SMP
[   21.135917] Modules linked in:
[   21.136085] CPU: 1 UID: 0 PID: 1735 Comm: dup-lazyfree Not tainted 7.0.0-rc1-00116-g018018a17770 #1028 PREEMPT
[   21.136858] Hardware name: linux,dummy-virt (DT)
[   21.137019] pstate: 21400005 (nzCv daif +PAN -UAO -TCO +DIT -SSBS BTYPE=--)
[   21.137308] pc : page_table_check_set+0x28c/0x2a8
[   21.137607] lr : page_table_check_set+0x134/0x2a8
[   21.137885] sp : ffff80008a3b3340
[   21.138124] x29: ffff80008a3b3340 x28: fffffdffc3d14400 x27: ffffd1a55e03d000
[   21.138623] x26: 0040000000000040 x25: ffffd1a55f7dd000 x24: 0000000000000001
[   21.139045] x23: 0000000000000001 x22: 0000000000000001 x21: ffffd1a55f217f30
[   21.139629] x20: 0000000000134521 x19: 0000000000134519 x18: 005c43e000040000
[   21.140027] x17: 0001400000000000 x16: 0001700000000000 x15: 000000000000ffff
[   21.140578] x14: 000000000000000c x13: 005c006000000000 x12: 0000000000000020
[   21.140828] x11: 0000000000000000 x10: 005c000000000000 x9 : ffffd1a55c079ee0
[   21.141077] x8 : 0000000000000001 x7 : 005c03e000040000 x6 : 000000004000ffff
[   21.141490] x5 : ffff00017fffce00 x4 : 0000000000000001 x3 : 0000000000000002
[   21.141741] x2 : 0000000000134510 x1 : 0000000000000000 x0 : ffff0000c08228c0
[   21.141991] Call trace:
[   21.142093]  page_table_check_set+0x28c/0x2a8 (P)
[   21.142265]  __page_table_check_ptes_set+0x144/0x1e8
[   21.142441]  __set_ptes_anysz.constprop.0+0x160/0x1a8
[   21.142766]  contpte_set_ptes+0xe8/0x140
[   21.142907]  try_to_unmap_one+0x10c4/0x10d0
[   21.143177]  rmap_walk_anon+0x100/0x250
[   21.143315]  try_to_unmap+0xa0/0xc8
[   21.143441]  shrink_folio_list+0x59c/0x18a8
[   21.143759]  shrink_lruvec+0x664/0xbf0
[   21.144043]  shrink_node+0x218/0x878
[   21.144285]  __node_reclaim.constprop.0+0x98/0x338
[   21.144763]  user_proactive_reclaim+0x2a4/0x340
[   21.145056]  reclaim_store+0x3c/0x60
[   21.145216]  dev_attr_store+0x20/0x40
[   21.145585]  sysfs_kf_write+0x84/0xa8
[   21.145835]  kernfs_fop_write_iter+0x130/0x1c8
[   21.145994]  vfs_write+0x2b8/0x368
[   21.146119]  ksys_write+0x70/0x110
[   21.146240]  __arm64_sys_write+0x24/0x38
[   21.146380]  invoke_syscall+0x50/0x120
[   21.146513]  el0_svc_common.constprop.0+0x48/0xf8
[   21.146679]  do_el0_svc+0x28/0x40
[   21.146798]  el0_svc+0x34/0x110
[   21.146926]  el0t
---truncated---

## References
- https://git.kernel.org/stable/c/29f40594a28114b9a9bc87f6cf7bbee9609628f2
- https://git.kernel.org/stable/c/99888a4f340ca8e839a0524556bd4db76d63f4e0
- https://git.kernel.org/stable/c/a0911ccdba41b0871abbf8412857bafedec3dbe1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
