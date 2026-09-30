# [M] sched/core: Disable page allocation in task_tick_mm_cid()

## Summary
Severity: Medium
Advisory: CVE-2024-50140
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-50140
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.59, >=6.7.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/core: Disable page allocation in task_tick_mm_cid()

With KASAN and PREEMPT_RT enabled, calling task_work_add() in
task_tick_mm_cid() may cause the following splat.

[   63.696416] BUG: sleeping function called from invalid context at kernel/locking/spinlock_rt.c:48
[   63.696416] in_atomic(): 1, irqs_disabled(): 1, non_block: 0, pid: 610, name: modprobe
[   63.696416] preempt_count: 10001, expected: 0
[   63.696416] RCU nest depth: 1, expected: 1

This problem is caused by the following call trace.

  sched_tick() [ acquire rq->__lock ]
   -> task_tick_mm_cid()
    -> task_work_add()
     -> __kasan_record_aux_stack()
      -> kasan_save_stack()
       -> stack_depot_save_flags()
        -> alloc_pages_mpol_noprof()
         -> __alloc_pages_noprof()
	  -> get_page_from_freelist()
	   -> rmqueue()
	    -> rmqueue_pcplist()
	     -> __rmqueue_pcplist()
	      -> rmqueue_bulk()
	       -> rt_spin_lock()

The rq lock is a raw_spinlock_t. We can't sleep while holding
it. IOW, we can't call alloc_pages() in stack_depot_save_flags().

The task_tick_mm_cid() function with its task_work_add() call was
introduced by commit 223baf9d17f2 ("sched: Fix performance regression
introduced by mm_cid") in v6.4 kernel.

Fortunately, there is a kasan_record_aux_stack_noalloc() variant that
calls stack_depot_save_flags() while not allowing it to allocate
new pages.  To allow task_tick_mm_cid() to use task_work without
page allocation, a new TWAF_NO_ALLOC flag is added to enable calling
kasan_record_aux_stack_noalloc() instead of kasan_record_aux_stack()
if set. The task_tick_mm_cid() function is modified to add this new flag.

The possible downside is the missing stack trace in a KASAN report due
to new page allocation required when task_work_add_noallloc() is called
which should be rare.

## References
- https://git.kernel.org/stable/c/509c29d0d26f68a6f6d0a05cb1a89725237e2b87
- https://git.kernel.org/stable/c/73ab05aa46b02d96509cb029a8d04fca7bbde8c7
- https://git.kernel.org/stable/c/ce0241ef83eed55f675376e8a3605d23de53d875
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50140.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50140
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
