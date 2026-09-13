# [C] nvmet-tcp: fix race between ICReq handling and queue teardown

## Summary
Severity: Critical
Advisory: CVE-2026-46135
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46135
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.144, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

nvmet-tcp: fix race between ICReq handling and queue teardown

nvmet_tcp_handle_icreq() updates queue->state after sending an
Initialization Connection Response (ICResp), but it does so without
serializing against target-side queue teardown.

If an NVMe/TCP host sends an Initialization Connection Request
(ICReq) and immediately closes the connection, target-side teardown
may start in softirq context before io_work drains the already
buffered ICReq. In that case, nvmet_tcp_schedule_release_queue()
sets queue->state to NVMET_TCP_Q_DISCONNECTING and drops the queue
reference under state_lock.

If io_work later processes that ICReq, nvmet_tcp_handle_icreq() can
still overwrite the state back to NVMET_TCP_Q_LIVE. That defeats the
DISCONNECTING-state guard in nvmet_tcp_schedule_release_queue() and
allows a later socket state change to re-enter teardown and issue a
second kref_put() on an already released queue.

The ICResp send failure path has the same problem. If teardown has
already moved the queue to DISCONNECTING, a send error can still
overwrite the state with NVMET_TCP_Q_FAILED, again reopening the
window for a second teardown path to drop the queue reference.

Fix this by serializing both post-send state transitions with
state_lock and bailing out if teardown has already started.

Use -ESHUTDOWN as an internal sentinel for that bail-out path rather
than propagating it as a transport error like -ECONNRESET. Keep
nvmet_tcp_socket_error() setting rcv_state to NVMET_TCP_RECV_ERR before
honoring that sentinel so receive-side parsing stays quiesced until the
existing release path completes.

## References
- https://git.kernel.org/stable/c/49891c8fe0cb43fbbe480da1cdccfbbaeb820cb3
- https://git.kernel.org/stable/c/5293a8882c549fab4a878bc76b0b6c951f980a61
- https://git.kernel.org/stable/c/5f0b95ef68ab9afba75b20eebf436130f80c161a
- https://git.kernel.org/stable/c/67e1aaf93b495c2f10bc8a5fbba575fbb7f449b6
- https://git.kernel.org/stable/c/6f96dea4819d122737b217ea16660d255abbf8c6
- https://git.kernel.org/stable/c/9c63cf80895a70eb4fcfcaa725bb1ac9ae76f02b
- https://git.kernel.org/stable/c/b7dd4d27aa70bd98bb10572310e913668baf6a65
- https://git.kernel.org/stable/c/dcfe4d1f7960e7d1c01642318f3aae1a604f8508
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46135.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46135
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
