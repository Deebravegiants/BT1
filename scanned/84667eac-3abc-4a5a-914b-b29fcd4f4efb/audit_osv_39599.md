# [H] procfs: fix missing RCU protection when reading real_parent in do_task_stat()

## Summary
Severity: High
Advisory: CVE-2026-46259
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-03
Source: https://osv.dev/vulnerability/CVE-2026-46259
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.252, >=5.11.0 <5.15.202, >=5.16.0 <6.1.165, >=6.2.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.14, >=6.19.0 <6.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

procfs: fix missing RCU protection when reading real_parent in do_task_stat()

When reading /proc/[pid]/stat, do_task_stat() accesses task->real_parent
without proper RCU protection, which leads to:

  cpu 0                               cpu 1
  -----                               -----
  do_task_stat
    var = task->real_parent
                                      release_task
                                        call_rcu(delayed_put_task_struct)
    task_tgid_nr_ns(var)
      rcu_read_lock   <--- Too late to protect task->real_parent!
      task_pid_ptr    <--- UAF!
      rcu_read_unlock

This patch uses task_ppid_nr_ns() instead of task_tgid_nr_ns() to add
proper RCU protection for accessing task->real_parent.

## References
- https://git.kernel.org/stable/c/0e64bd46a04a4fd61279aca9f53a664e9e5f7e7e
- https://git.kernel.org/stable/c/1c8dc5b5517546c68ffae40b948336122bb61306
- https://git.kernel.org/stable/c/4f9ae386861e280b7631ca252f798d25575627ee
- https://git.kernel.org/stable/c/73ec7c96601d61d52310c659145bb06d933a0fa6
- https://git.kernel.org/stable/c/76149d53502cf17ef3ae454ff384551236fba867
- https://git.kernel.org/stable/c/c93a33f28f915d446eea6fb3f0e1def0b3af1982
- https://git.kernel.org/stable/c/dd8b13cb4ff1a4545a214ed897fdf2bc341155b6
- https://git.kernel.org/stable/c/fefa0fcd78be465b7ad4c497fa6ec90d64194c04
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46259.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46259
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
