# [H] sched_ext: Skip sub-disable teardown for never-linked sub-schedulers

## Summary
Severity: High
Advisory: CVE-2026-74731
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74731
Type: osv

## Affected
- Linux: `Kernel` — affected >=7.1.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

sched_ext: Skip sub-disable teardown for never-linked sub-schedulers

A sub-scheduler enable can fail before scx_link_sched() links the sched into
the hierarchy, e.g. when the parent is already being disabled, and cleanup
still runs the full scx_sub_disable().

That is racy against root disable: drain_descendants() is the only ordering
between a sub's disable-time task walk and root disable's all-task teardown,
and an unlinked sub is invisible to it. Root's teardown can thus run between
the never-linked sub's drain and its walk, exiting every task to no
scheduler.

The walk then trips the membership WARN and re-homes the exited tasks onto
the dying hierarchy, a use-after-free.

Skip the cgroup ownership reset and the task walk if @sch was never linked,
indicated by the empty ->sibling as unlinking only happens later in the same
function. The membership WARN remains valid: a linked sub is always waited
on by an ancestor's drain.

## References
- https://git.kernel.org/stable/c/6428093a4a986c38c9089b5eb32b56d914ef437a
- https://git.kernel.org/stable/c/8c13364db9c9a43ed286f3a8d0fb9477b1adc43c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74731.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
