# [C] ipv6: addrconf: bail out of dad_failure when state is no longer POSTDAD

## Summary
Severity: Critical
Advisory: CVE-2026-74398
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74398
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: addrconf: bail out of dad_failure when state is no longer POSTDAD

addrconf_dad_failure() transitions ifp->state from DAD to POSTDAD
via addrconf_dad_end(), which drops ifp->lock on return.  The lock
is re-acquired after net_info_ratelimited().  A concurrent
ipv6_del_addr() can take the lock in that window, set ifp->state
to DEAD and run list_del_rcu(&ifp->if_list).

addrconf_dad_failure() then overwrites DEAD with ERRDAD at errdad:
and schedules a new dad_work.  The work calls ipv6_del_addr()
again, hitting the already-poisoned list entry:

  general protection fault: 0000 [#1] SMP NOPTI
  CPU: 4 PID: 217 Comm: kworker/4:1
  Workqueue: ipv6_addrconf addrconf_dad_work
  RIP: 0010:ipv6_del_addr+0xe9/0x280
  RAX: dead000000000122
  Call Trace:
   addrconf_dad_stop+0x113/0x140
   addrconf_dad_work+0x28c/0x430
   process_one_work+0x1eb/0x3b0
   worker_thread+0x4d/0x400
   kthread+0x104/0x140
   ret_from_fork+0x35/0x40

Fold the addrconf_dad_end() logic into addrconf_dad_failure() under
a single ifp->lock critical section.  The STABLE_PRIVACY branch
temporarily drops ifp->lock around address regeneration, so at
lock_errdad: verify the state is still POSTDAD before transitioning
to ERRDAD; bail out otherwise to avoid overwriting a state set by
another path while the lock was released.

## References
- https://git.kernel.org/stable/c/3bdc86d89fd6c6523753fa6f42fcfaf30ee699cb
- https://git.kernel.org/stable/c/47b05836705b63dab93d9ac7c69a3a507375ef80
- https://git.kernel.org/stable/c/627ac78f2741e2ebd2225e2e953b6964a8a9182f
- https://git.kernel.org/stable/c/875c284c0f98b042bb97abad460f63a24c977f88
- https://git.kernel.org/stable/c/8ed0ce9ea58d677d1bac92614ee5f60f8ea57363
- https://git.kernel.org/stable/c/b61af0268e3d1308c466bf0be5dced844eafc1ef
- https://git.kernel.org/stable/c/d21be7d051012c6b572fa4e3334443c250216f7b
- https://git.kernel.org/stable/c/e889aa99ad3ed48bb0ddcff6475b17542532d18b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74398.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74398
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
