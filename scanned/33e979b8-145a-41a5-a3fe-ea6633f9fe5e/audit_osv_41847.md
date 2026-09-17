# [H] net/handshake: Use spin_lock_bh for hn_lock

## Summary
Severity: High
Advisory: CVE-2026-63980
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63980
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/handshake: Use spin_lock_bh for hn_lock

nvmet_tcp_state_change(), a socket callback that runs in BH context,
can reach handshake_req_cancel() via nvmet_tcp_schedule_release_queue()
and tls_handshake_cancel().  handshake_req_cancel() acquires
hn->hn_lock with plain spin_lock().  If a process-context thread on
the same CPU holds hn->hn_lock when a softirq invokes the cancel path,
the lock attempt deadlocks.  This is the only caller that invokes
tls_handshake_cancel() from BH context; every other consumer calls it
from process context.

Deferring the cancel to process context in the NVMe target is not
straightforward: nvmet_tcp_schedule_release_queue() must call
tls_handshake_cancel() atomically with its state transition to
DISCONNECTING.  If the cancel were deferred, the handshake completion
callback could fire in the window before the cancel runs, observe the
unexpected state, and return without dropping its kref on the queue.
Reworking that interlock is considerably more invasive than hardening
the handshake lock.  Convert all hn->hn_lock acquisitions from
spin_lock/spin_unlock to spin_lock_bh/spin_unlock_bh so the lock is
never taken with softirqs enabled.

## References
- https://git.kernel.org/stable/c/06ab5978866fc2221b910347fd3e510ca8e7b1a4
- https://git.kernel.org/stable/c/0866569fc36a56f568acd3900d354e3505932e09
- https://git.kernel.org/stable/c/91898de9501a047ba67c6b864dcd403e00bdfbf5
- https://git.kernel.org/stable/c/cc993e0927ec8bd98ea33377ada03295fcda0f24
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63980.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63980
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
