# [H] sched/psi: use kernfs polling functions for PSI trigger polling

## Summary
Severity: High
Advisory: CVE-2023-54019
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-24
Source: https://osv.dev/vulnerability/CVE-2023-54019
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <6.1.42, >=6.2.0 <6.4.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched/psi: use kernfs polling functions for PSI trigger polling

Destroying psi trigger in cgroup_file_release causes UAF issues when
a cgroup is removed from under a polling process. This is happening
because cgroup removal causes a call to cgroup_file_release while the
actual file is still alive. Destroying the trigger at this point would
also destroy its waitqueue head and if there is still a polling process
on that file accessing the waitqueue, it will step on the freed pointer:

do_select
  vfs_poll
                           do_rmdir
                             cgroup_rmdir
                               kernfs_drain_open_files
                                 cgroup_file_release
                                   cgroup_pressure_release
                                     psi_trigger_destroy
                                       wake_up_pollfree(&t->event_wait)
// vfs_poll is unblocked
                                       synchronize_rcu
                                       kfree(t)
  poll_freewait -> UAF access to the trigger's waitqueue head

Patch [1] fixed this issue for epoll() case using wake_up_pollfree(),
however the same issue exists for synchronous poll() case.
The root cause of this issue is that the lifecycles of the psi trigger's
waitqueue and of the file associated with the trigger are different. Fix
this by using kernfs_generic_poll function when polling on cgroup-specific
psi triggers. It internally uses kernfs_open_node->poll waitqueue head
with its lifecycle tied to the file's lifecycle. This also renders the
fix in [1] obsolete, so revert it.

[1] commit c2dbe32d5db5 ("sched/psi: Fix use-after-free in ep_remove_wait_queue()")

## References
- https://git.kernel.org/stable/c/92cc0153324b6ae8577a39f5bf2cd83c9a34ea6a
- https://git.kernel.org/stable/c/aff037078ecaecf34a7c2afab1341815f90fba5e
- https://git.kernel.org/stable/c/d124ab17024cc85a1079b7810a018a497ebc13da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54019.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54019
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
