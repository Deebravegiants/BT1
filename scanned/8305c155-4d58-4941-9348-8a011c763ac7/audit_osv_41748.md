# [H] sched/mmcid: Fix OOB clear_bit when CID is MM_CID_UNSET in fixup path

## Summary
Severity: High
Advisory: CVE-2026-63799
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63799
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/mmcid: Fix OOB clear_bit when CID is MM_CID_UNSET in fixup path

In mm_cid_fixup_cpus_to_tasks(), when rq->curr has the target mm and
mm_cid.active is set, the CID is checked with cid_in_transit() before
setting the transition bit.  In per-CPU mode a newly forked or exec'd
task can be running with mm_cid.cid == MM_CID_UNSET because CIDs are
assigned lazily on schedule-in.  With cid_in_transit() the guard passes
for MM_CID_UNSET (no transit bit), converts it to MM_CID_UNSET |
MM_CID_TRANSIT and stores it back; later mm_cid_schedout() feeds this
to clear_bit() with MM_CID_UNSET as the bit number, triggering an
out-of-bounds write.

Symptoms: this is genuine memory corruption, but a bounded out-of-bounds
write, not an arbitrary one.  MM_CID_UNSET is the fixed sentinel BIT(31),
so once the bad value reaches mm_cid_schedout() the cid_from_transit_cid()
strip leaves MM_CID_UNSET, which fails the "cid < max_cids" convergence
test and falls into mm_drop_cid() -> clear_bit(MM_CID_UNSET,
mm_cidmask(mm)).  The cid bitmap is embedded in the mm_struct slab object
(after cpu_bitmap and mm_cpus_allowed) and is only num_possible_cpus()
bits wide, so clearing bit 31 is a deterministic OOB bit-clear at a
fixed offset of 2^31 / 8 == 256 MiB past the bitmap base.  The address is
not attacker-influenced (fixed sentinel -> fixed offset) and the op only
clears a single bit; what sits 256 MiB further along the direct map is
whatever kernel object happens to live there, so this corrupts one bit of
unpredictable kernel memory -- it is not an arbitrary-address or
arbitrary-value write.

It triggers only in per-CPU CID mode, when a CPU is running an active
task of the target mm whose cid is still MM_CID_UNSET -- the
fork()/execve() window before that task's next schedule-in assigns it a
real CID -- and a per-CPU -> per-task fixup walks over it (the mode
fallback driven by a thread exit, sched_mm_cid_exit(), or by the deferred
max_cids recompute in mm_cid_work_fn()).

In practice syzkaller surfaced it as a KASAN use-after-free reported in
__schedule -> mm_cid_switch_to, where the offending clear_bit() is inlined
via mm_cid_schedout() -> mm_drop_cid().

Guard the transition-bit assignment against MM_CID_UNSET, in addition to
the existing cid_in_transit() check, so the bit is only set on a genuine
task-owned CID.  A CPU-owned (MM_CID_ONCPU) CID of a running active task
is handled by the cid_on_cpu(pcp->cid) branch above and never reaches
this path, so excluding MM_CID_UNSET (and the already-transitioning case)
is sufficient.

## References
- https://git.kernel.org/stable/c/8d32856fb72ba976d9c87ba405fd17e80419934c
- https://git.kernel.org/stable/c/de3ab9bd3133899efb92e4cd05ba4203e58fc0a3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63799.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
