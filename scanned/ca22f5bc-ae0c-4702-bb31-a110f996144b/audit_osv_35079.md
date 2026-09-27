# [H] veth: more robust handing of race to avoid txq getting stuck

## Summary
Severity: High
Advisory: CVE-2025-68232
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-12-16
Source: https://osv.dev/vulnerability/CVE-2025-68232
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: more robust handing of race to avoid txq getting stuck

Commit dc82a33297fc ("veth: apply qdisc backpressure on full ptr_ring to
reduce TX drops") introduced a race condition that can lead to a permanently
stalled TXQ. This was observed in production on ARM64 systems (Ampere Altra
Max).

The race occurs in veth_xmit(). The producer observes a full ptr_ring and
stops the queue (netif_tx_stop_queue()). The subsequent conditional logic,
intended to re-wake the queue if the consumer had just emptied it (if
(__ptr_ring_empty(...)) netif_tx_wake_queue()), can fail. This leads to a
"lost wakeup" where the TXQ remains stopped (QUEUE_STATE_DRV_XOFF) and
traffic halts.

This failure is caused by an incorrect use of the __ptr_ring_empty() API
from the producer side. As noted in kernel comments, this check is not
guaranteed to be correct if a consumer is operating on another CPU. The
empty test is based on ptr_ring->consumer_head, making it reliable only for
the consumer. Using this check from the producer side is fundamentally racy.

This patch fixes the race by adopting the more robust logic from an earlier
version V4 of the patchset, which always flushed the peer:

(1) In veth_xmit(), the racy conditional wake-up logic and its memory barrier
are removed. Instead, after stopping the queue, we unconditionally call
__veth_xdp_flush(rq). This guarantees that the NAPI consumer is scheduled,
making it solely responsible for re-waking the TXQ.
  This handles the race where veth_poll() consumes all packets and completes
NAPI *before* veth_xmit() on the producer side has called netif_tx_stop_queue.
The __veth_xdp_flush(rq) will observe rx_notify_masked is false and schedule
NAPI.

(2) On the consumer side, the logic for waking the peer TXQ is moved out of
veth_xdp_rcv() and placed at the end of the veth_poll() function. This
placement is part of fixing the race, as the netif_tx_queue_stopped() check
must occur after rx_notify_masked is potentially set to false during NAPI
completion.
  This handles the race where veth_poll() consumes all packets, but haven't
finished (rx_notify_masked is still true). The producer veth_xmit() stops the
TXQ and __veth_xdp_flush(rq) will observe rx_notify_masked is true, meaning
not starting NAPI.  Then veth_poll() change rx_notify_masked to false and
stops NAPI.  Before exiting veth_poll() will observe TXQ is stopped and wake
it up.

## References
- https://git.kernel.org/stable/c/5442a9da69789741bfda39f34ee7f69552bf0c56
- https://git.kernel.org/stable/c/6c8a8b9257a660e622689e23c8fbad4ba2b561b9
- https://git.kernel.org/stable/c/dd419a3f2ebc18cc00bc32c57fd052d7a188b78b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68232.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68232
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
