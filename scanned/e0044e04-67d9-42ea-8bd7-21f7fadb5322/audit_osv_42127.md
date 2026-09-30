# [H] posix-cpu-timers: Prevent UAF caused by non-leader exec() race

## Summary
Severity: High
Advisory: CVE-2026-64560
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-64560
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.262, >=5.11.0 <5.15.213, >=5.16.0 <6.1.180, >=6.2.0 <6.6.147, >=6.7.0 <6.12.100, >=6.13.0 <6.18.41, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

posix-cpu-timers: Prevent UAF caused by non-leader exec() race

Wongi and Jungwoo decoded and reported a non-leader exec() related race
which can result in an UAF:

 sys_timer_delete()			exec()
   posix_cpu_timer_del()
   // Observes old leader
   p = pid_task(pid, pid_type);		de_thread()
   					  switch_leader();
					  release_task(old_leader)
					    __exit_signal(old_leader)
					      sighand = lock(old_leader, sighand);
					      posix_cpu_timers*_exit();
   sighand = lock_task_sighand(p)	      unhash_task(old_leader);
     sh = lock(p, sighand)	    	      old_leader->sighand = NULL;
					      unlock(sighand);
     (p->sighand == NULL)
	unlock(sh)
	return NULL;

   // Returns without action
   if(!sighand)
      return 0;
   free_posix_timer();

This is "harmless" unless the deleted timer was armed and enqueued in
p->signal because on exec() a TGID targeted timer is inherited.

As sys_timer_delete() freed the underlying posix timer object
run_posix_cpu_timers() or any timerqueue related add/delete operations on
other timers will access the freed object's timerqueue node, which results
in an UAF.

There is a similar problem vs. posix_cpu_timer_set(). For regular posix
timers it just transiently returns -ESRCH to user space, but for the use
case in do_cpu_nanosleep() it's the same UAF just that the k_itimer is
allocated on the stack.

Also posix_cpu_timer_rearm() fails to rearm the timer, which means it stops
to expire.

While debating solutions Frederic pointed out another problem:

   posix_cpu_timer_del(tmr)
					__exit_signal(p)
					  posix_cpu_timers*_exit(p);
					  unhash_task(p);
					  p->sighand = NULL;
     sh = lock_task_sighand(p)
        sighand = p->sighand;
	if (!sighand)
	    return NULL;
	lock(sighand);

     if (!sh)
	WARN_ON_ONCE(timer_queued(tmr));

On weakly ordered architectures it is not guaranteed that
posix_cpu_timer_del() will observe the stores in posix_cpu_timers*_exit()
when p->sighand is observed as NULL, which means the WARN() can be a false
positive.

Solve these issues by:

  1) Changing the store in __exit_signal() to smp_store_release().

  2) Adding a smp_acquire__after_ctrl_dep() into the !sighand path
     of lock_task_sighand().

  3) Creating a helper function for looking up the task and locking sighand
     which does not return when sighand == NULL. Instead it retries the
     task lookup and only if that fails it gives up.

  4) Using that helper in the three affected functions.

#1/#2 ensures that the reader side which observes sighand == NULL also
observes all preceeding stores, i.e. the stores in posix_cpu_timers*_exit()
and the ones in unhash_task().

#3 ensures that the above described non-leader exec() situation is handled
gracefully. When the task lookup returns the old leader, but sighand ==
NULL then it retries. In the non-leader exec() case the subsequent task
lookup will observe the new leader due to #1/#2. In normal exit() scenarios
the subsequent lookup fails.

When the task lookup fails, the function also checks whether the timer is
still enqueued and issues a warning if that's the case. Unfortunately there
is nothing which can be done about it, but as the task is already not
longer visible the timer should not be accessed anymore. This check also
requires memory ordering, which is not provided when the first lookup
fails. To achieve that the check is preceeded by a smp_rmb() which pairs
with the smp_wmb() in write_seqlock() in __exit_signal(). That ensures that
the stores in posix_cpu_timers*_exit() are visible.

The history of the non-leader exec() issue goes back to the early days of
posix CPU timers, which stored a pointer to the group leader task in the
timer. That obviously fails when a non-leader exec() switches the leader.
commit e0a70217107e ("posix-cpu-timers: workaround to suppress the problems
with mt exec") added a temporary workaround for that in 2010 which surv
---truncated---

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/12a891c773aeb5823d63dbd0cb2ab931d6c21c9b
- https://git.kernel.org/stable/c/67aa823e3e8c229c6d374df79c804f6721cb83b6
- https://git.kernel.org/stable/c/6a7ecc25abe6f0fecc6e62a05096987200edbd02
- https://git.kernel.org/stable/c/920f893f735e92ba3a1cd9256899a186b161928d
- https://git.kernel.org/stable/c/ad1cafa1bdaa71da85d71cac053838bbe97852b6
- https://git.kernel.org/stable/c/cc35ddbc497311e0b6b9a6a6a4f4d1217d6ab1aa
- https://git.kernel.org/stable/c/d8bcb28abad857f1415da7656f19b2ada90af04f
- https://git.kernel.org/stable/c/e74443f5db0037c556ef436fa64b88bf4ea08f83
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64560.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64560
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
