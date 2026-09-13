# [H] perf: Reject exited events as group leaders

## Summary
Severity: High
Advisory: CVE-2026-74753
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74753
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.145 <6.6.156, >=6.12.96 <6.12.108, >=6.18.39 <6.18.46, >=7.1.4 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf: Reject exited events as group leaders

perf_event_remove_on_exec() sets remove-on-exec events to the EXIT state
and detaches their group relationships.  The event's file descriptor can
remain open, however, and perf_event_open() currently accepts that event
as a group leader because its early validation rejects only REVOKED and
DEAD events.

A new sibling can consequently be linked to the detached leader.  When
the leader is closed, perf_group_detach() observes that its
PERF_ATTACH_GROUP bit is already clear and skips the new sibling.  The
sibling then retains a group_leader pointer to the freed event.

Reject group leaders in the EXIT state.  Perform the check while holding
the shared context mutex so that an exec in the target task cannot detach
the leader between validation and group attachment.

[peterz: make the earlier test fully consistent]

## References
- https://git.kernel.org/stable/c/7a03413f31c196ab3894f988cdce0bb47b4fec42
- https://git.kernel.org/stable/c/7ce010275c531475f9d6e7efb11b9e522c74ed2e
- https://git.kernel.org/stable/c/ce12e1170c0c78dffb9b28af6d287492ae7dd99d
- https://git.kernel.org/stable/c/e593031ff19a9484e8a00bc47edd447187721846
- https://git.kernel.org/stable/c/fa091f46c3833fb22384f10eade2b4e1e1d0b278
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74753.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74753
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
