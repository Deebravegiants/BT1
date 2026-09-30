# [H] mrp: introduce active flags to prevent UAF when applicant uninit

## Summary
Severity: High
Advisory: CVE-2022-50697
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2022-50697
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

mrp: introduce active flags to prevent UAF when applicant uninit

The caller of del_timer_sync must prevent restarting of the timer, If
we have no this synchronization, there is a small probability that the
cancellation will not be successful.

And syzbot report the fellowing crash:
==================================================================
BUG: KASAN: use-after-free in hlist_add_head include/linux/list.h:929 [inline]
BUG: KASAN: use-after-free in enqueue_timer+0x18/0xa4 kernel/time/timer.c:605
Write at addr f9ff000024df6058 by task syz-fuzzer/2256
Pointer tag: [f9], memory tag: [fe]

CPU: 1 PID: 2256 Comm: syz-fuzzer Not tainted 6.1.0-rc5-syzkaller-00008-
ge01d50cbd6ee #0
Hardware name: linux,dummy-virt (DT)
Call trace:
 dump_backtrace.part.0+0xe0/0xf0 arch/arm64/kernel/stacktrace.c:156
 dump_backtrace arch/arm64/kernel/stacktrace.c:162 [inline]
 show_stack+0x18/0x40 arch/arm64/kernel/stacktrace.c:163
 __dump_stack lib/dump_stack.c:88 [inline]
 dump_stack_lvl+0x68/0x84 lib/dump_stack.c:106
 print_address_description mm/kasan/report.c:284 [inline]
 print_report+0x1a8/0x4a0 mm/kasan/report.c:395
 kasan_report+0x94/0xb4 mm/kasan/report.c:495
 __do_kernel_fault+0x164/0x1e0 arch/arm64/mm/fault.c:320
 do_bad_area arch/arm64/mm/fault.c:473 [inline]
 do_tag_check_fault+0x78/0x8c arch/arm64/mm/fault.c:749
 do_mem_abort+0x44/0x94 arch/arm64/mm/fault.c:825
 el1_abort+0x40/0x60 arch/arm64/kernel/entry-common.c:367
 el1h_64_sync_handler+0xd8/0xe4 arch/arm64/kernel/entry-common.c:427
 el1h_64_sync+0x64/0x68 arch/arm64/kernel/entry.S:576
 hlist_add_head include/linux/list.h:929 [inline]
 enqueue_timer+0x18/0xa4 kernel/time/timer.c:605
 mod_timer+0x14/0x20 kernel/time/timer.c:1161
 mrp_periodic_timer_arm net/802/mrp.c:614 [inline]
 mrp_periodic_timer+0xa0/0xc0 net/802/mrp.c:627
 call_timer_fn.constprop.0+0x24/0x80 kernel/time/timer.c:1474
 expire_timers+0x98/0xc4 kernel/time/timer.c:1519

To fix it, we can introduce a new active flags to make sure the timer will
not restart.

## References
- https://git.kernel.org/stable/c/1a185fe83c2a60c1e3596fb9d82dbeb148dc09c6
- https://git.kernel.org/stable/c/563e45fd5046045cc194af3ba17f5423e1c98170
- https://git.kernel.org/stable/c/5d5a481a7fd0234f617535dc464ea010804a1129
- https://git.kernel.org/stable/c/755eb0879224ffc2a43de724554aeaf0e51e5a64
- https://git.kernel.org/stable/c/78d48bc41f7726113c9f114268d3ab11212814da
- https://git.kernel.org/stable/c/98f53e591940e4c3818be358c5dc684d5b30cb56
- https://git.kernel.org/stable/c/aacffc1a8dbf67c5463cb4f67b37143c01ca6fa9
- https://git.kernel.org/stable/c/aadb1507a77b060c529edfeaf67f803e31461f24
- https://git.kernel.org/stable/c/ab0377803dafc58f1e22296708c1c28e309414d6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50697.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50697
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
