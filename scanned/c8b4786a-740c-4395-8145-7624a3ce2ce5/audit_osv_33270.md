# [H] futex: Prevent use-after-free during requeue-PI

## Summary
Severity: High
Advisory: CVE-2025-39977
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-15
Source: https://osv.dev/vulnerability/CVE-2025-39977
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.155, >=6.2.0 <6.6.109, >=6.7.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

futex: Prevent use-after-free during requeue-PI

syzbot managed to trigger the following race:

   T1                               T2

 futex_wait_requeue_pi()
   futex_do_wait()
     schedule()
                               futex_requeue()
                                 futex_proxy_trylock_atomic()
                                   futex_requeue_pi_prepare()
                                   requeue_pi_wake_futex()
                                     futex_requeue_pi_complete()
                                      /* preempt */

         * timeout/ signal wakes T1 *

   futex_requeue_pi_wakeup_sync() // Q_REQUEUE_PI_LOCKED
   futex_hash_put()
  // back to userland, on stack futex_q is garbage

                                      /* back */
                                     wake_up_state(q->task, TASK_NORMAL);

In this scenario futex_wait_requeue_pi() is able to leave without using
futex_q::lock_ptr for synchronization.

This can be prevented by reading futex_q::task before updating the
futex_q::requeue_state. A reference on the task_struct is not needed
because requeue_pi_wake_futex() is invoked with a spinlock_t held which
implies a RCU read section.

Even if T1 terminates immediately after, the task_struct will remain valid
during T2's wake_up_state().  A READ_ONCE on futex_q::task before
futex_requeue_pi_complete() is enough because it ensures that the variable
is read before the state is updated.

Read futex_q::task before updating the requeue state, use it for the
following wakeup.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/348736955ed6ca6e99ca24b93b1d3fbfe352c181
- https://git.kernel.org/stable/c/a170b9c0dde83312b8b58ccc91509c7c15711641
- https://git.kernel.org/stable/c/b549113738e8c751b613118032a724b772aa83f2
- https://git.kernel.org/stable/c/cb5d19a61274b51b49601214a87af573b43d60fa
- https://git.kernel.org/stable/c/d824b2dbdcfe3c390278dd9652ea526168ef6850
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39977.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39977
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
