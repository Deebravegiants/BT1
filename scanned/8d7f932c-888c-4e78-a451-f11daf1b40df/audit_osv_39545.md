# [H] xfrm: defensively unhash xfrm_state lists in __xfrm_state_delete

## Summary
Severity: High
Advisory: CVE-2026-46116
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46116
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.19 <5.10.261, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: defensively unhash xfrm_state lists in __xfrm_state_delete

KASAN reproduces a slab-use-after-free in __xfrm_state_delete()'s
hlist_del_rcu calls under syzkaller load on linux-6.12.y stable
(reproduced on 6.12.47, also reachable via the same code path on
torvalds/master and on the ipsec tree). Nine unique signatures cluster
in the xfrm_state lifecycle, the load-bearing one being:

  BUG: KASAN: slab-use-after-free in __hlist_del include/linux/list.h:990 [inline]
  BUG: KASAN: slab-use-after-free in hlist_del_rcu include/linux/rculist.h:516 [inline]
  BUG: KASAN: slab-use-after-free in __xfrm_state_delete net/xfrm/xfrm_state.c
  Write of size 8 at addr ffff8881198bcb70 by task kworker/u8:9/435

  Workqueue: netns cleanup_net
  Call Trace:
   __hlist_del / hlist_del_rcu
   __xfrm_state_delete
   xfrm_state_delete
   xfrm_state_flush
   xfrm_state_fini
   ops_exit_list
   cleanup_net

The other observed signatures hit the same slab object from
__xfrm_state_lookup, xfrm_alloc_spi, __xfrm_state_insert and an OOB
write variant of __xfrm_state_delete, all on the byseq/byspi
hash chains.

__xfrm_state_delete() guards its byseq and byspi unhashes with
value-based predicates:

	if (x->km.seq)
		hlist_del_rcu(&x->byseq);
	if (x->id.spi)
		hlist_del_rcu(&x->byspi);

while everywhere else in the file (e.g. state_cache, state_cache_input)
the safer hlist_unhashed() check is used. xfrm_alloc_spi() sets
x->id.spi = newspi inside xfrm_state_lock and then immediately inserts
into byspi, but a path that observes x->id.spi != 0 outside of
xfrm_state_lock can still skip-or-hit the byspi unhash inconsistently
with whether x is actually on the list. The same holds for x->km.seq
versus byseq, and the bydst/bysrc unhashes have no predicate at all,
so a second __xfrm_state_delete() on the same object writes through
LIST_POISON pprev.

The defensive change here:

  - Use hlist_del_init_rcu() instead of hlist_del_rcu() on bydst,
    bysrc, byseq and byspi so a second deletion is a no-op rather
    than a write through LIST_POISON pprev. The byseq/byspi nodes
    are already initialised in xfrm_state_alloc().
  - Test hlist_unhashed() rather than the value predicate for
    byseq/byspi, so the unhash decision tracks list state rather than
    mutable scalar fields.

Empirical verification: applied this patch on top of v6.12.47, rebuilt,
and re-ran the same syzkaller harness for 1h16m on a previously-crashy
configuration that produced ~100 hits each of slab-use-after-free
Read in xfrm_alloc_spi / Read in __xfrm_state_lookup / Write in
__xfrm_state_delete. After the patch, 7.1M execs across 32 VMs at
~1550 exec/sec produced zero xfrm_state UAF/OOB hits. /proc/slabinfo
confirms the xfrm_state slab is actively allocated and freed during
the run (~143 KiB resident), so the fuzzer is still exercising those
code paths -- they just no longer crash.

Reproduction:

  - Linux 6.12.47 x86_64 + KASAN_GENERIC + KASAN_INLINE + KCOV
  - syzkaller @ 746545b8b1e4c3a128db8652b340d3df90ce61db
  - 32 QEMU/KVM VMs x 2 vCPU on AWS c5.metal bare metal
  - 9 unique signatures collected in ~9h, all within xfrm_state
    lifecycle

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/14acf9652e5690de3c7486c6db5fb8dafd0a32a3
- https://git.kernel.org/stable/c/26edb0a3c99f9d958c212be68b21f1221614dcf0
- https://git.kernel.org/stable/c/2c617848ae6e4f07a3e397f604208c293bbecacc
- https://git.kernel.org/stable/c/3943fcad7694a7d0b15aeabe7d3cc2a2eb8e92e8
- https://git.kernel.org/stable/c/4980162de555cb838f1a189ce7d2cbf5d2e7b050
- https://git.kernel.org/stable/c/6b4dc3181b4bfc5f5fc33ab33b1dc6e15759f4b6
- https://git.kernel.org/stable/c/a2e2d08fb070fab4947447171f1c4e3ca5a188e5
- https://git.kernel.org/stable/c/b4a53add2fa8f1b5aa17d4c5686c320785fab182
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46116.json
- https://access.redhat.com/errata/RHSA-2026:36018
- https://access.redhat.com/errata/RHSA-2026:39179
- https://access.redhat.com/errata/RHSA-2026:39180
- https://access.redhat.com/errata/RHSA-2026:39371
- https://access.redhat.com/errata/RHSA-2026:41234
- https://access.redhat.com/errata/RHSA-2026:41235
- https://access.redhat.com/errata/RHSA-2026:42919
- https://access.redhat.com/errata/RHSA-2026:43231
- https://access.redhat.com/errata/RHSA-2026:44385
- https://access.redhat.com/errata/RHSA-2026:47632
