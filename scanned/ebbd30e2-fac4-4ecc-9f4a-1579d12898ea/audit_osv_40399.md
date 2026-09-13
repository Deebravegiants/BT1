# [H] vsock/virtio: fix potential unbounded skb queue

## Summary
Severity: High
Advisory: CVE-2026-53132
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53132
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: fix potential unbounded skb queue

virtio_transport_inc_rx_pkt() checks vvs->rx_bytes + len > vvs->buf_alloc.

virtio_transport_recv_enqueue() skips coalescing for packets
with VIRTIO_VSOCK_SEQ_EOM.

If fed with packets with len == 0 and VIRTIO_VSOCK_SEQ_EOM,
a very large number of packets can be queued
because vvs->rx_bytes stays at 0.

Fix this by estimating the skb metadata size:

	(Number of skbs in the queue) * SKB_TRUESIZE(0)

## References
- https://git.kernel.org/stable/c/059b7dbd20a6f0c539a45ddff1573cb8946685b5
- https://git.kernel.org/stable/c/100d5b2ffdc6468b9e48532641f29e83efdcb63c
- https://git.kernel.org/stable/c/1eca304f97a34ed5e921e1f0e06c8b241f25bf12
- https://git.kernel.org/stable/c/9bdc637fde66b63d6cad0caacd034888bb7bf5f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53132.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53132
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
