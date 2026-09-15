# [H] net/sched: act_tunnel_key: Defer dst_release to RCU callback

## Summary
Severity: High
Advisory: CVE-2026-68377
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68377
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_tunnel_key: Defer dst_release to RCU callback

Fix a race-condition use-after-free in tunnel_key_release_params().

The function releases the metadata_dst of the old params synchronously
via dst_release() while deferring the params struct free with
kfree_rcu(). A concurrent tunnel_key_act() reader on the datapath may
still hold the old params pointer (under rcu_read_lock_bh) and proceed
to call dst_clone(&params->tcft_enc_metadata->dst) after the writer's
dst_release has already pushed the dst's rcuref to RCUREF_DEAD.

zdi-disclosures@trendmicro.com produced a poc which i (and Victor) verified
that KASAN reports:

==================================================================
BUG: KASAN: slab-use-after-free in instrument_atomic_read_write include/linux/instrumented.h:112
BUG: KASAN: slab-use-after-free in atomic_sub_return_release include/linux/atomic/atomic-instrumented.h:326
BUG: KASAN: slab-use-after-free in __rcuref_put include/linux/rcuref.h:109
BUG: KASAN: slab-use-after-free in rcuref_put include/linux/rcuref.h:173
BUG: KASAN: slab-use-after-free in dst_release+0x5b/0x370 net/core/dst.c:168
Write of size 4 at addr ffff88806158de40 by task poc/9388

CPU: 0 UID: 0 PID: 9388 Comm: poc Tainted: G        W           7.1.0-rc7 #7 PREEMPT(lazy)
Tainted: [W]=WARN
Hardware name: QEMU Ubuntu 25.10 PC v2 (i440FX + PIIX, + 10.1 machine, 1996), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
Call Trace:
 <TASK>
 __dump_stack lib/dump_stack.c:94
 dump_stack_lvl+0x100/0x190 lib/dump_stack.c:120
 print_address_description mm/kasan/report.c:378
 print_report+0x139/0x4ad mm/kasan/report.c:482
 kasan_report+0xe4/0x1d0 mm/kasan/report.c:595
 check_region_inline mm/kasan/generic.c:186
 kasan_check_range+0x125/0x200 mm/kasan/generic.c:200
 instrument_atomic_read_write include/linux/instrumented.h:112
 atomic_sub_return_release include/linux/atomic/atomic-instrumented.h:326
 __rcuref_put include/linux/rcuref.h:109
 rcuref_put include/linux/rcuref.h:173
 dst_release+0x5b/0x370 net/core/dst.c:168
 refdst_drop include/net/dst.h:272
 skb_dst_drop include/net/dst.h:284
 skb_release_head_state+0x293/0x400 net/core/skbuff.c:1163
 skb_release_all net/core/skbuff.c:1187
[..]
Allocated by task 9391:
 kasan_save_stack+0x30/0x50 mm/kasan/common.c:57
 kasan_save_track+0x14/0x30 mm/kasan/common.c:78
 poison_kmalloc_redzone mm/kasan/common.c:398
 __kasan_kmalloc+0x9a/0xb0 mm/kasan/common.c:415
 kasan_kmalloc include/linux/kasan.h:263
 __do_kmalloc_node mm/slub.c:5296
 __kmalloc_noprof+0x2f1/0x830 mm/slub.c:5308
 kmalloc_noprof include/linux/slab.h:954
 kzalloc_noprof include/linux/slab.h:1188
 offload_action_alloc+0x2f/0x130 net/core/flow_offload.c:35
 tcf_action_offload_add_ex+0x1ba/0x880 net/sched/act_api.c:258
 tcf_action_offload_add net/sched/act_api.c:293
 tcf_action_init+0x66e/0xa20 net/sched/act_api.c:1547
 tcf_action_add+0xf6/0x5d0 net/sched/act_api.c:2101
[..]
Freed by task 9391:
 kasan_save_stack+0x30/0x50 mm/kasan/common.c:57
 kasan_save_track+0x14/0x30 mm/kasan/common.c:78
 kasan_save_free_info+0x3b/0x70 mm/kasan/generic.c:584
 poison_slab_object mm/kasan/common.c:253
 __kasan_slab_free+0x6b/0x90 mm/kasan/common.c:285
 kasan_slab_free include/linux/kasan.h:235
 slab_free_hook mm/slub.c:2689
 slab_free mm/slub.c:6251
 kfree+0x21f/0x6b0 mm/slub.c:6566
 tcf_action_offload_add_ex+0x4ad/0x880 net/sched/act_api.c:284
 tcf_action_offload_add net/sched/act_api.c:293
 tcf_action_init+0x66e/0xa20 net/sched/act_api.c:1547
 tcf_action_add+0xf6/0x5d0 net/sched/act_api.c:2101

The buggy address belongs to the object at ffff88806158de00
 which belongs to the cache kmalloc-256 of size 256
The buggy address is located 64 bytes inside of
 freed 256-byte region [ffff88806158de00, ffff88806158df00)

The buggy address belongs to the physical page:
page: refcount:0 mapcount:0 mapping:0000000000000000 index:0xffff88806158d600 pfn:0x6158c
head: order:1 mapcount:0 entire_map
---truncated---

## References
- https://git.kernel.org/stable/c/2200a00ff247f70f5dcdb4e6f14b0d48ddac5467
- https://git.kernel.org/stable/c/2791a501da508b704a617b4dba29db54a65bc9f7
- https://git.kernel.org/stable/c/389d03992dabb80488228e8119b9dd6d0f58e1a6
- https://git.kernel.org/stable/c/531dbb5bb98e52ad26be7e90f9f8bec707c5bd0e
- https://git.kernel.org/stable/c/676ad6aa7cec89a08d2a5ce3cd5959e313f29733
- https://git.kernel.org/stable/c/b5931f020b681fdcb9378262d89b61cb3c7ebbf8
- https://git.kernel.org/stable/c/f1f5c8a3955f8fda3f84ed883ac8daa1847e724c
- https://git.kernel.org/stable/c/fed1b1ddab41a0e7a462ac690a0c8af6ff793624
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68377.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68377
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
