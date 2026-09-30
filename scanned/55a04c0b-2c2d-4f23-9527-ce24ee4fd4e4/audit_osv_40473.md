# [H] ipv6: mcast: Fix use-after-free when processing MLD queries

## Summary
Severity: High
Advisory: CVE-2026-53275
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53275
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.15 <5.10.269, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: mcast: Fix use-after-free when processing MLD queries

When processing an MLD query, a pointer to the multicast group address
is retrieved when initially parsing the packet. This pointer is later
dereferenced without being reloaded despite the fact that the skb header
might have been reallocated following the pskb_may_pull() calls, leading
to a use-after-free [1].

Fix by copying the multicast group address when the packet is initially
parsed.

[1]
BUG: KASAN: slab-use-after-free in __mld_query_work (net/ipv6/mcast.c:1512)
Read of size 8 at addr ffff8881154b8e90 by task kworker/4:1/118

Workqueue: mld mld_query_work
Call Trace:
<TASK>
dump_stack_lvl (lib/dump_stack.c:94 lib/dump_stack.c:120)
print_address_description.constprop.0 (mm/kasan/report.c:378)
print_report (mm/kasan/report.c:482)
kasan_report (mm/kasan/report.c:595)
__mld_query_work (net/ipv6/mcast.c:1512)
mld_query_work (net/ipv6/mcast.c:1563)
process_one_work (kernel/workqueue.c:3314)
worker_thread (kernel/workqueue.c:3397 kernel/workqueue.c:3478)
kthread (kernel/kthread.c:436)
ret_from_fork (arch/x86/kernel/process.c:158)
ret_from_fork_asm (arch/x86/entry/entry_64.S:245)
</TASK>

[...]

Freed by task 118:
kasan_save_stack (mm/kasan/common.c:57)
kasan_save_track (mm/kasan/common.c:78)
kasan_save_free_info (mm/kasan/generic.c:584)
__kasan_slab_free (mm/kasan/common.c:253 mm/kasan/common.c:285)
kfree (./include/linux/kasan.h:235 mm/slub.c:2689 mm/slub.c:6251 mm/slub.c:6566)
pskb_expand_head (net/core/skbuff.c:2335)
__pskb_pull_tail (net/core/skbuff.c:2878 (discriminator 4))
__mld_query_work (net/ipv6/mcast.c:1495 (discriminator 1))
mld_query_work (net/ipv6/mcast.c:1563)
process_one_work (kernel/workqueue.c:3314)
worker_thread (kernel/workqueue.c:3397 kernel/workqueue.c:3478)
kthread (kernel/kthread.c:436)
ret_from_fork (arch/x86/kernel/process.c:158)
ret_from_fork_asm (arch/x86/entry/entry_64.S:245)

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/087dbacf897c020f438f780f0a4a8aa73b6d7c5a
- https://git.kernel.org/stable/c/1354271c89d0e5fbf8b3d94097ff0216695209c7
- https://git.kernel.org/stable/c/2a613bf497029d555a7428406aa8cdb84a503cea
- https://git.kernel.org/stable/c/4203806f700bb44ea0b05d484d9d40044b47fb04
- https://git.kernel.org/stable/c/53baa63a4183291574483f89583dbef13677a2c4
- https://git.kernel.org/stable/c/791c91dc7a9dfb2457d5e29b8216a6484b9c4b40
- https://git.kernel.org/stable/c/b2eb8886200b907fc71806869620609f0f4cacb0
- https://git.kernel.org/stable/c/dfaf1f5e7eb81be87582bd6a57d34e61a57d5dea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53275.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53275
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
