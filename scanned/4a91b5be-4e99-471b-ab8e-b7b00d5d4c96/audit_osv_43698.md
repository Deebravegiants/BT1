# [H] sched/psi: Shut down rtpoll_timer in psi_cgroup_free()

## Summary
Severity: High
Advisory: CVE-2026-74594
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74594
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.266, >=5.11.0 <5.15.217, >=5.14.0 <6.1.183, >=5.16.0 <6.6.152, >=6.2.0 <6.12.104, >=6.7.0 <6.18.45, >=6.13.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/psi: Shut down rtpoll_timer in psi_cgroup_free()

psi_schedule_rtpoll_work() is called locklessly from the scheduler hotpath
and can race psi_trigger_destroy() taking down the last rtpoll trigger under
rtpoll_trigger_lock:

  psi_schedule_rtpoll_work()        psi_trigger_destroy()

  rcu_read_lock();
  task = rcu_dereference(rtpoll_task);
                                    rcu_assign_pointer(rtpoll_task, NULL);
                                    timer_delete(&rtpoll_timer);
  mod_timer(&rtpoll_timer, ...);
  rcu_read_unlock();
                                    synchronize_rcu();
                                    kthread_stop(task_to_destroy);

The group can then be freed with the re-armed timer still pending, and
poll_timer_fn() runs on freed memory.

461daba06bdc ("psi: eliminate kthread_worker from psi trigger scheduling
mechanism") deleted the timer synchronously after the synchronize_rcu(),
which prevented this but raced trigger creation instead: the deletion could
cancel the timer that a new trigger set armed during the grace period and,
as creation also reinitialized the timer at the time, corrupt it.
8f91efd870ea ("psi: Fix race between psi_trigger_create/destroy") moved the
initialization into group_init() and the deletion into the locked section,
trading the creation races for the window above.

Neither placement in the destruction path works. A pending timer firing
while the group is alive is harmless though. poll_timer_fn() just wakes the
rtpoll waitqueue and doesn't re-arm itself. Bind the timer to the group's
lifetime instead and shut it down in psi_cgroup_free(). Nothing can arm it
by then. timer_shutdown_sync() because the timer is never armed again.

## References
- https://git.kernel.org/stable/c/1e5ca82eee59caca6988f9d6e859786aab8a5fa0
- https://git.kernel.org/stable/c/310b5a537a78c358a4cd244bd767c1a517a05459
- https://git.kernel.org/stable/c/4addb102154b7cf6e2310ccbe20c3c08619e520d
- https://git.kernel.org/stable/c/5457025fa8ca3c0d2732109513de839e3e797190
- https://git.kernel.org/stable/c/611e7821c4f83a671455658797336faecc3a5196
- https://git.kernel.org/stable/c/8037c5b2b2a447df52542f4d8535895d837bdcbd
- https://git.kernel.org/stable/c/806fcff98c1d7cb3c1dc0015e55ebdbe819e6b08
- https://git.kernel.org/stable/c/894a9300d7fb2e2951da92e565ae6de7ddfb0a69
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74594.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74594
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
