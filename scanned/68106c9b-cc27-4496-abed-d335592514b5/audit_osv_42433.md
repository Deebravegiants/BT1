# [H] net/sched: serialize qdisc_rtab_list against concurrent get/put

## Summary
Severity: High
Advisory: CVE-2026-68138
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68138
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.46, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: serialize qdisc_rtab_list against concurrent get/put

qdisc_get_rtab() and qdisc_put_rtab() mutate the process-global singly
linked list qdisc_rtab_list and a plain non-atomic 'int refcnt' with no
lock. This was only safe because every caller historically held the RTNL
mutex, which serialized all rate-table lookups, inserts and frees.

That invariant no longer holds. cls_flower sets
TCF_PROTO_OPS_DOIT_UNLOCKED, so tc_new_tfilter() keeps rtnl_held == false
for it and sets TCA_ACT_FLAGS_NO_RTNL. That flag propagates through
tcf_exts_validate_ex() -> tcf_action_init() -> tcf_action_init_1() ->
tcf_police_init(), which calls qdisc_get_rtab()/qdisc_put_rtab() with the
RTNL mutex NOT held. Two RTM_NEWTFILTER requests on different CPUs, each
adding a flower filter with a police action carrying the same rate, then
race on qdisc_rtab_list and on the non-atomic refcnt, leading to a
use-after-free / double-free of the kmalloc-2k struct qdisc_rate_table.
qdisc_rtab_list is a single global (not per-netns), so the corrupted
object is shared system-wide.

  BUG: KASAN: slab-use-after-free in qdisc_put_rtab+0x12f/0x160
   qdisc_put_rtab+0x12f/0x160
   tcf_police_init+0xda9/0x1590
   tcf_action_init_1+0x460/0x6b0
   tcf_action_init+0x439/0xa40
   tcf_exts_validate_ex+0x42d/0x550
   fl_change+0xddd/0x7da0
   tc_new_tfilter+0xaa7/0x2420
   rtnetlink_rcv_msg+0x95e/0xe90
  which belongs to the cache kmalloc-2k of size 2048

Protect qdisc_rtab_list and the refcount with a dedicated spinlock. The
(sleeping, GFP_KERNEL) allocation in qdisc_get_rtab() is performed before
taking the lock; if a concurrent inserter added an identical table in the
meantime the freshly allocated one is freed under the lock, so no
duplicate is leaked. qdisc_put_rtab() now decrements the refcount and
unlinks under the same lock.

## References
- https://git.kernel.org/stable/c/1b050d09dd1a0ddae83bf012cf4956b7a960235f
- https://git.kernel.org/stable/c/4131dd0b6f67acddd616ed7c244e1d3eedd46e7b
- https://git.kernel.org/stable/c/6e0241f6cbb149d926ee8efee2c734fea71452cf
- https://git.kernel.org/stable/c/8ddc2eb0d2da9c83f54f1e5720525b461b8480c4
- https://git.kernel.org/stable/c/d981098b76756ed71666a27518eeb69883657c43
- https://git.kernel.org/stable/c/f43ee0c0730d6191629b5ee1ceae27b1ebfdc047
- https://git.kernel.org/stable/c/f93c89392bd3b180b5b7abc6fdae8e3dd667a313
- https://git.kernel.org/stable/c/fb29e1b41052488ee3f2d115d4a870497ebd7f7d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68138.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68138
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
