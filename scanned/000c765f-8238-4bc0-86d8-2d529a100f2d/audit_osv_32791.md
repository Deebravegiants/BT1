# [H] x86/mm: Eliminate window where TLB flushes may be inadvertently skipped

## Summary
Severity: High
Advisory: CVE-2025-37964
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37964
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.183, >=5.16.0 <6.1.139, >=6.2.0 <6.6.91, >=6.7.0 <6.12.29, >=6.13.0 <6.14.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

x86/mm: Eliminate window where TLB flushes may be inadvertently skipped

tl;dr: There is a window in the mm switching code where the new CR3 is
set and the CPU should be getting TLB flushes for the new mm.  But
should_flush_tlb() has a bug and suppresses the flush.  Fix it by
widening the window where should_flush_tlb() sends an IPI.

Long Version:

=== History ===

There were a few things leading up to this.

First, updating mm_cpumask() was observed to be too expensive, so it was
made lazier.  But being lazy caused too many unnecessary IPIs to CPUs
due to the now-lazy mm_cpumask().  So code was added to cull
mm_cpumask() periodically[2].  But that culling was a bit too aggressive
and skipped sending TLB flushes to CPUs that need them.  So here we are
again.

=== Problem ===

The too-aggressive code in should_flush_tlb() strikes in this window:

	// Turn on IPIs for this CPU/mm combination, but only
	// if should_flush_tlb() agrees:
	cpumask_set_cpu(cpu, mm_cpumask(next));

	next_tlb_gen = atomic64_read(&next->context.tlb_gen);
	choose_new_asid(next, next_tlb_gen, &new_asid, &need_flush);
	load_new_mm_cr3(need_flush);
	// ^ After 'need_flush' is set to false, IPIs *MUST*
	// be sent to this CPU and not be ignored.

        this_cpu_write(cpu_tlbstate.loaded_mm, next);
	// ^ Not until this point does should_flush_tlb()
	// become true!

should_flush_tlb() will suppress TLB flushes between load_new_mm_cr3()
and writing to 'loaded_mm', which is a window where they should not be
suppressed.  Whoops.

=== Solution ===

Thankfully, the fuzzy "just about to write CR3" window is already marked
with loaded_mm==LOADED_MM_SWITCHING.  Simply checking for that state in
should_flush_tlb() is sufficient to ensure that the CPU is targeted with
an IPI.

This will cause more TLB flush IPIs.  But the window is relatively small
and I do not expect this to cause any kind of measurable performance
impact.

Update the comment where LOADED_MM_SWITCHING is written since it grew
yet another user.

Peter Z also raised a concern that should_flush_tlb() might not observe
'loaded_mm' and 'is_lazy' in the same order that switch_mm_irqs_off()
writes them.  Add a barrier to ensure that they are observed in the
order they are written.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/02ad4ce144bd27f71f583f667fdf3b3ba0753477
- https://git.kernel.org/stable/c/12f703811af043d32b1c8a30001b2fa04d5cd0ac
- https://git.kernel.org/stable/c/399ec9ca8fc4999e676ff89a90184ec40031cf59
- https://git.kernel.org/stable/c/d41072906abec8bb8e01ed16afefbaa558908c89
- https://git.kernel.org/stable/c/d87392094f96e162fa5fa5a8640d70cc0952806f
- https://git.kernel.org/stable/c/fea4e317f9e7e1f449ce90dedc27a2d2a95bee5a
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37964.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37964
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
