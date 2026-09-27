# [H] powerpc/64s/slb: Fix SLB multihit issue during SLB preload

## Summary
Severity: High
Advisory: CVE-2025-71078
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-71078
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.248, >=5.11.0 <5.15.198, >=5.16.0 <6.1.160, >=6.2.0 <6.6.120, >=6.7.0 <6.12.64, >=6.13.0 <6.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/64s/slb: Fix SLB multihit issue during SLB preload

On systems using the hash MMU, there is a software SLB preload cache that
mirrors the entries loaded into the hardware SLB buffer. This preload
cache is subject to periodic eviction — typically after every 256 context
switches — to remove old entry.

To optimize performance, the kernel skips switch_mmu_context() in
switch_mm_irqs_off() when the prev and next mm_struct are the same.
However, on hash MMU systems, this can lead to inconsistencies between
the hardware SLB and the software preload cache.

If an SLB entry for a process is evicted from the software cache on one
CPU, and the same process later runs on another CPU without executing
switch_mmu_context(), the hardware SLB may retain stale entries. If the
kernel then attempts to reload that entry, it can trigger an SLB
multi-hit error.

The following timeline shows how stale SLB entries are created and can
cause a multi-hit error when a process moves between CPUs without a
MMU context switch.

CPU 0                                   CPU 1
-----                                    -----
Process P
exec                                    swapper/1
 load_elf_binary
  begin_new_exc
    activate_mm
     switch_mm_irqs_off
      switch_mmu_context
       switch_slb
       /*
        * This invalidates all
        * the entries in the HW
        * and setup the new HW
        * SLB entries as per the
        * preload cache.
        */
context_switch
sched_migrate_task migrates process P to cpu-1

Process swapper/0                       context switch (to process P)
(uses mm_struct of Process P)           switch_mm_irqs_off()
                                         switch_slb
                                           load_slb++
                                            /*
                                            * load_slb becomes 0 here
                                            * and we evict an entry from
                                            * the preload cache with
                                            * preload_age(). We still
                                            * keep HW SLB and preload
                                            * cache in sync, that is
                                            * because all HW SLB entries
                                            * anyways gets evicted in
                                            * switch_slb during SLBIA.
                                            * We then only add those
                                            * entries back in HW SLB,
                                            * which are currently
                                            * present in preload_cache
                                            * (after eviction).
                                            */
                                        load_elf_binary continues...
                                         setup_new_exec()
                                          slb_setup_new_exec()

                                        sched_switch event
                                        sched_migrate_task migrates
                                        process P to cpu-0

context_switch from swapper/0 to Process P
 switch_mm_irqs_off()
  /*
   * Since both prev and next mm struct are same we don't call
   * switch_mmu_context(). This will cause the HW SLB and SW preload
   * cache to go out of sync in preload_new_slb_context. Because there
   * was an SLB entry which was evicted from both HW and preload cache
   * on cpu-1. Now later in preload_new_slb_context(), when we will try
   * to add the same preload entry again, we will add this to the SW
   * preload cache and then will add it to the HW SLB. Since on cpu-0
   * this entry was never invalidated, hence adding this entry to the HW
   * SLB will cause a SLB multi-hit error.
   */
load_elf_binary cont
---truncated---

## References
- https://git.kernel.org/stable/c/00312419f0863964625d6dcda8183f96849412c6
- https://git.kernel.org/stable/c/01324c0328181b94cf390bda22ff91c75126ea57
- https://git.kernel.org/stable/c/2e9a95d60f1df7b57618fd5ef057aef331575bd2
- https://git.kernel.org/stable/c/4ae1e46d8a290319f33f71a2710a1382ba5431e8
- https://git.kernel.org/stable/c/895123c309a34d2cfccf7812b41e17261a3a6f37
- https://git.kernel.org/stable/c/b13a3dbfa196af68eae2031f209743735ad416bf
- https://git.kernel.org/stable/c/c9f865022a1823d814032a09906e91e4701a35fc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71078.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71078
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
