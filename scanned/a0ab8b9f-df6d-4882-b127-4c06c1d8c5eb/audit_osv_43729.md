# [H] perf/core: Fix group leader use-after-free after sibling detach

## Summary
Severity: High
Advisory: CVE-2026-74637
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74637
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.105, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Fix group leader use-after-free after sibling detach

perf_group_detach() handles leader and sibling detach differently. When the
group leader is detached, all siblings are promoted to singleton events and
their group_leader pointer is reset to themselves. When a sibling is
detached, it is removed from the leader's sibling_list, but its
group_leader pointer is left pointing at the old leader.

That is harmless when the sibling is being closed and freed immediately, as
in the DETACH_DEAD path. It is not safe when the sibling is detached but
kept alive, such as during CPU hotplug with DETACH_GROUP. In that case the
sibling is removed from the context, while its file descriptor can still
keep it alive.

A typical failing sequence is:

  - A group contains leader L and sibling S.
  - CPU hot-unplug detaches S with DETACH_GROUP, removing it from
    L->sibling_list but leaving S->group_leader == L.
  - L is later closed and freed.
  - A PERF_IOC_FLAG_GROUP ioctl on S follows S->group_leader and
    dereferences the freed leader.

This was reproduced by running the perf event fuzzer, CPU hotplug, and a
stress workload concurrently:

  Unable to handle kernel paging request at virtual address 006b6b6b6b6b6cdb
  CPU: 2 PID: 12489 Comm: perf_fuzzer 6.18.7 PREEMPT
  pc : perf_ioctl+0x34c/0xc68
  x20: ffffff89a3fa2c70 x8 : 6b6b6b6b6b6b6b6b
  Code: 943c4a0e 340047a0 f9404a94 f9411e88 (f940b908)
  Call trace:
  perf_ioctl+0x34c/0xc68 (P)
  __arm64_sys_ioctl+0xa0/0xf4
  invoke_syscall+0x58/0xe4
  el0_svc_common+0xa8/0xdc
  do_el0_svc+0x1c/0x28
  el0_svc+0x40/0xc0
  el0t_64_sync_handler+0x68/0xdc
  el0t_64_sync+0x1c4/0x1c8

The fault happened in perf_ioctl(), where perf_event_for_each() follows
the stale group_leader pointer and perf_event_for_each_child() then
dereferences the freed leader's context.

Fix the use-after-free by promoting the detached sibling to a singleton.
Also fix __event_disable() cgroup accounting and event state change.

## References
- https://git.kernel.org/stable/c/1e7abfeb23c12bf46f6457e4a3e1a1a300d50619
- https://git.kernel.org/stable/c/42c5ca1f0a288a52878bd72a5595b08261057438
- https://git.kernel.org/stable/c/80c6054a4c40a0ffad82acef9f9a0dee108d152a
- https://git.kernel.org/stable/c/8e92e03984364d93e0d5b0acd81c95eca773f034
- https://git.kernel.org/stable/c/8f867c0e8da4c2303d91adf45acb6b1820966c27
- https://git.kernel.org/stable/c/a979a642402d0b1f856c7a729b4cb2d92de4cf2f
- https://git.kernel.org/stable/c/b42948f9e0d1ea4dbd5742ce1dfc7688de5d4a35
- https://git.kernel.org/stable/c/f8a07021679aadfb6d63b209207ccc41f26982d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74637.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74637
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
