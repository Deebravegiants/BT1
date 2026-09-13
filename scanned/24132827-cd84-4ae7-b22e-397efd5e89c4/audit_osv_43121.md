# [C] net/9p: fix race condition on rdma->state in trans_rdma.c

## Summary
Severity: Critical
Advisory: CVE-2026-72491
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72491
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/9p: fix race condition on rdma->state in trans_rdma.c

The rdma->state field is modified without holding req_lock in both
recv_done() and p9_cm_event_handler(), while rdma_request() accesses
the same field under the req_lock spinlock. This inconsistent locking
creates a race condition:

- recv_done() running in softirq completion context sets
  rdma->state = P9_RDMA_FLUSHING without acquiring req_lock

- p9_cm_event_handler() modifies rdma->state at multiple points
  (ADDR_RESOLVED, ROUTE_RESOLVED, ESTABLISHED, CLOSED) without
  req_lock

- rdma_request() uses spin_lock_irqsave(&rdma->req_lock, flags) to
  protect the read-modify-write of rdma->state

The race can cause lost state transitions: recv_done() or the CM
event handler could set state to FLUSHING/CLOSED while rdma_request()
is concurrently checking or modifying state under the lock, leading to
the FLUSHING transition being silently overwritten by CLOSING. This
corrupts the connection state machine and can cause use-after-free on
RDMA request objects during teardown.

Fix by adding req_lock protection to all rdma->state modifications in
recv_done() and p9_cm_event_handler(), matching the pattern already
used in rdma_request(). Use spin_lock_irqsave/spin_unlock_irqrestore
in the CM event handler since it can race with recv_done() which runs
in softirq context.

Tested with a kernel module that races two threads (simulating
rdma_request and recv_done/CM handler) on rdma->state with proper
locking: 5.5M+ FLUSHING writes over 27M iterations with 0 lost
transitions.

## References
- https://git.kernel.org/stable/c/13bf9879b778b2f4b260b45bed18f31806120d1e
- https://git.kernel.org/stable/c/151f8cf5b23d8a534d884432a82a6d54d5a61989
- https://git.kernel.org/stable/c/3970a19a80de530b801b6256354d4a529a9a2d6c
- https://git.kernel.org/stable/c/4cee2b8766045059d5e0b8114837b4a8efe827ac
- https://git.kernel.org/stable/c/5424138848eb7d7d8a7196676e90a2cbf2142454
- https://git.kernel.org/stable/c/7d54894a1ee265a72d70f7cae1da6cc774cccc71
- https://git.kernel.org/stable/c/8aadc136d8e8d8fc95d7982d213cfe2234dfcf2b
- https://git.kernel.org/stable/c/ebbcbe5c0db215feecc17def06178da443f4eea6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72491.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72491
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
