# [C] rxrpc: Fix call timer start racing with call destruction

## Summary
Severity: Critical
Advisory: CVE-2022-49149
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49149
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix call timer start racing with call destruction

The rxrpc_call struct has a timer used to handle various timed events
relating to a call.  This timer can get started from the packet input
routines that are run in softirq mode with just the RCU read lock held.
Unfortunately, because only the RCU read lock is held - and neither ref or
other lock is taken - the call can start getting destroyed at the same time
a packet comes in addressed to that call.  This causes the timer - which
was already stopped - to get restarted.  Later, the timer dispatch code may
then oops if the timer got deallocated first.

Fix this by trying to take a ref on the rxrpc_call struct and, if
successful, passing that ref along to the timer.  If the timer was already
running, the ref is discarded.

The timer completion routine can then pass the ref along to the call's work
item when it queues it.  If the timer or work item where already
queued/running, the extra ref is discarded.

## References
- https://git.kernel.org/stable/c/051360e51341cd17738d82c15a8226010c7cb7f6
- https://git.kernel.org/stable/c/4a7f62f91933c8ae5308f9127fd8ea48188b6bc3
- https://git.kernel.org/stable/c/54df5a37f1d951ed27fd47bf9b15a42279582110
- https://git.kernel.org/stable/c/5e3c11144e557a9dbf9a2f6abe444689ef9d8aae
- https://git.kernel.org/stable/c/8cbf4ae7a2833767d63114573e5f9a45740cc975
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49149.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49149
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
