# [C] locking/rt: Fix the incorrect RCU protection in rt_spin_unlock()

## Summary
Severity: Critical
Advisory: CVE-2026-72069
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72069
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

locking/rt: Fix the incorrect RCU protection in rt_spin_unlock()

rt_spin_unlock() releases the RCU protection before unlocking the
lock. That opens the door for the following UAF scenario:

 T1					T2
 spin_lock(&p->lock);		rcu_read_lock();
 invalidate(p);			p = rcu_dereference(ptr);
 rcu_assign_pointer(ptr, NULL);	if (!p) return;
 spin_unlock(&p->lock);		spin_lock(&p->lock)
 				   lock(&lock->lock);
				   rcu_read_lock();
 kfree_rcu(p);			rcu_read_unlock();
				....
				spin_unlock(&p->lock)
				  rcu_read_unlock(); // Ends grace period
 rcu_do_batch()
   kfree(p);
			    UAF ->	  rt_mutex_cmpxchg_release(&lock->lock...)

Regular spinlocks keep preemption disabled accross the unlock operation,
which provides full RCU protection, but the RT substitution fails to
resemble that. Same applies for the rwlock substitution.

Move the rcu_read_unlock() invocation past the unlock operations to match
the non-RT semantics. This makes it asymmetric vs. rt_xxx_lock(), but
that's harmless as the caller needs to hold RCU read lock across the lock
operation. The migrate_enable() call stays before the unlock operation
because there is no per CPU operation in the unlock path which would
require migration to be kept disabled.

## References
- https://git.kernel.org/stable/c/1f0d56d3f1e88f20f6e46109402f8c15d59bac37
- https://git.kernel.org/stable/c/3cfaac77b3c32ac3940df28866de263c3f45d24c
- https://git.kernel.org/stable/c/633cadbc0b8323f5cc140a285d2432089dbb534e
- https://git.kernel.org/stable/c/83f9fb561c1c3917e19f95523dd933c7d30291aa
- https://git.kernel.org/stable/c/89038cc87d80c77e7aa6f42a64b2573b74af339f
- https://git.kernel.org/stable/c/9d1fcd64ab81200e02b7a6db5eb1da8e244e8289
- https://git.kernel.org/stable/c/af28d801cd2db4cc7378554499bd4a5d84a5517e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72069.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72069
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
