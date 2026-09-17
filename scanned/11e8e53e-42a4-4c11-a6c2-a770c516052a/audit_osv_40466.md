# [H] net/sched: act_api: use RCU with deferred freeing for action lifecycle

## Summary
Severity: High
Advisory: CVE-2026-53264
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53264
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/sched: act_api: use RCU with deferred freeing for action lifecycle

When NEWTFILTER and DELFILTER are run concurrently it is possible to create a
race with an associated action.

Let's illustrate with CPU0 running NEWTFILTER and CPU1 running DELFILTER:

 0: mutex_lock() <-- holds the idr lock
 0: rcu_read_lock()
 0: p = idr_find(idr, index) <-- action p is valid (RCU protects IDR)
 0: mutex_unlock() <-- releases the idr lock
 1: refcount_dec_and_mutex_lock() <-- refcnt 1->0, mutex held
 1: idr_remove(idr, index) <-- Action removed from IDR
 1: mutex_unlock() <-- mutex released allowing us to delete the action
 1: tcf_action_cleanup(p); kfree(p) <-- Kfrees p immediately, no deferral
 0: refcount_inc_not_zero(&p->tcfa_refcnt) <-- ouch, UAF p points to freed memory

This patch fixes the race condition between NEWTFILTER and DELFILTER by
adding struct rcu_head to tc_action used in the deferral and introducing a
call_rcu() in the delete path to defer the final kfree().

Note: this is a revert of commit d7fb60b9cafb ("net_sched: get rid of tcfa_rcu")
but also modernization/simplification to directly use kfree_rcu().

Let's illustrate the new restored code path:

 0: rcu_read_lock()
 1: refcount_dec_and_mutex_lock() <-- refcnt 1->0, mutex held
 1: idr_remove(idr, index)
 1: mutex_unlock()
 1: call_rcu(&p->tcfa_rcu, tcf_action_rcu_free) <-- defer kfree after grace period
 0: p = idr_find(idr, index)
 0: refcount_inc_not_zero(&p->tcfa_refcnt) <-- fails, refcnt already 0
 1: rcu_read_unlock() <-- release so freeing can run after grace period

After CPU1 calls idr_remove(), the object is no longer reachable through the IDR.
CPU0's subsequent idr_find() will return NULL, and even if it still held a
stale pointer, the immediate kfree() is now deferred until after the RCU grace
period, so no UAF can occur.

## References
- https://git.kernel.org/stable/c/18af5d2ef0c4f65787fd1280c8b23286b9f2a835
- https://git.kernel.org/stable/c/1f1b98fea6b9ea30507d0f2fbff6750292d097e2
- https://git.kernel.org/stable/c/5057e1aca011e51ef51498c940ef96f3d3e8a305
- https://git.kernel.org/stable/c/5dd51e09020c65aa53cf128e5e3517cd53b3c113
- https://git.kernel.org/stable/c/8b136f18ac4b2ace5aaad3305b3f8a5d8165a009
- https://git.kernel.org/stable/c/91d105d2cbe002f9c7b43a6183adedc37e1da1f7
- https://git.kernel.org/stable/c/98b2e40879abf0245be5a5b7af69e0f6ff524ac3
- https://git.kernel.org/stable/c/b60e9391142e983fab2be53497aa8f71fdd09cd5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53264.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://starlabs.sg/blog/2026/07-when-ai-makes-0-days-feel-like-n-days/
