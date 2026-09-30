# [H] perf/core: Detach event groups during remove_on_exec

## Summary
Severity: High
Advisory: CVE-2026-64556
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-64556
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf/core: Detach event groups during remove_on_exec

perf_event_remove_on_exec() removes events by calling
perf_event_exit_event(). For top-level events, this removes the event from
the context with DETACH_EXIT only.

This can leave inconsistent group state when a removed event is a group
leader and the group contains siblings without remove_on_exec. If the group
was active, the surviving siblings can remain active and attached to the
removed leader's sibling list, but are no longer represented by a valid
group leader on the PMU context active lists.

A later close of the removed leader uses DETACH_GROUP and can promote the
still-active siblings from this stale group state. The next schedule-in can
then add an already-linked active_list entry again, corrupting the PMU
context active list.

With DEBUG_LIST enabled, this is caught as a list_add double-add in
merge_sched_in().

Fix this by detaching group relationships when remove_on_exec removes an
event. This preserves the existing task-exit and revoke behavior, while
ensuring surviving siblings are ungrouped before the removed event leaves
the context.

## References
- https://git.kernel.org/stable/c/037a3c43edfb597665dd34457cd22b14692f2ba3
- https://git.kernel.org/stable/c/06ccef0434e98058ddae7bcebc901f93d22b7653
- https://git.kernel.org/stable/c/39358e856fb89e62e3c8d7389a2dc4ec33dbe90e
- https://git.kernel.org/stable/c/4cdb1b3ab96eb1b7eb70bc5c82fede334bd60df2
- https://git.kernel.org/stable/c/a2d5d3ee7b6e3953114726b1521e62123ab5b043
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64556.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64556
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
