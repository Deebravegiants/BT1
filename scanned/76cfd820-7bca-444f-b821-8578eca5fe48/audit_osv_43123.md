# [C] net: serialize netif_running() check in enqueue_to_backlog()

## Summary
Severity: Critical
Advisory: CVE-2026-72493
Ecosystem: Linux
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72493
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: serialize netif_running() check in enqueue_to_backlog()

Syzbot reported a KASAN slab-use-after-free in fib_rules_lookup().

The root cause is a race condition where packets can escape the backlog
flushing during device unregistration (e.g., during netns exit).

Commit e9e4dd3267d0 ("net: do not process device backlog during unregistration")
introduced a lockless netif_running() check in enqueue_to_backlog() to
prevent queuing packets to an unregistering device.

However, this creates a TOCTOU race window.

A lockless transmitter (like veth_xmit) can pass
the check before dev_close() clears IFF_UP. If the transmitter is then
delayed, flush_all_backlogs() can run and finish before the transmitter
grabs the backlog lock and queues the packet. The packet then escapes
the flush and triggers UAF later when processed.

Fix this by moving the netif_running() check inside the backlog lock.
This serializes the check with the flush work (which also grabs the lock).
We then either queue the packet before the flush runs (so it gets flushed),
or check netif_running() after the flush/close completes (so it gets dropped).

## References
- https://git.kernel.org/stable/c/2fface6e0bbd6314d1d9d071abf2c4d67548511c
- https://git.kernel.org/stable/c/46762cefe7f4e5bffc1eb467810a7bbb02e461d7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72493.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72493
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
