# [H] sched_ext: Read scx_root under scx_cgroup_ops_rwsem in cgroup setters

## Summary
Severity: High
Advisory: CVE-2026-46154
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46154
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.32, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: Read scx_root under scx_cgroup_ops_rwsem in cgroup setters

scx_group_set_{weight,idle,bandwidth}() cache scx_root before acquiring
scx_cgroup_ops_rwsem, so the pointer can be stale by the time the op runs.
If the loaded scheduler is disabled and freed (via RCU work) and another is
enabled between the naked load and the rwsem acquire, the reader sees
scx_cgroup_enabled=true (the new scheduler's) but dereferences the freed one
- UAF on SCX_HAS_OP(sch, ...) / SCX_CALL_OP(sch, ...).

scx_cgroup_enabled is toggled only under scx_cgroup_ops_rwsem write
(scx_cgroup_{init,exit}), so reading scx_root inside the rwsem read section
correlates @sch with the enabled snapshot.

## References
- https://git.kernel.org/stable/c/0f54f6355575971673d8aac7da107ec4178e45bd
- https://git.kernel.org/stable/c/80afd4c84bc8f5e80145ce35279f5ce53f6043db
- https://git.kernel.org/stable/c/ce9aaa3af445c391735c9d000c4db60dfd5640d4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46154.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46154
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
