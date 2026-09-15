# [H] veth: fix queue index used to wake the peer txq in veth_poll

## Summary
Severity: High
Advisory: CVE-2026-74742
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74742
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.12.105, >=6.13.0 <6.18.46, >=6.16.0 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

veth: fix queue index used to wake the peer txq in veth_poll

veth_poll() derives the index of the peer TX queue to wake from
rq->xdp_rxq.queue_index. That field is only initialized by
xdp_rxq_info_reg() in veth_enable_xdp_range(), which runs only when an
XDP program is attached. On the plain GRO/NAPI path
(veth_napi_enable_range()) xdp_rxq_info_reg() is never called, so
queue_index stays 0 for every queue, as priv->rq is zero-allocated.

So in a multi-queue setup with GRO enabled and no XDP program attached,
every NAPI instance looks at the peer's TX queue 0. If veth_xmit() stops
peer TX queue 1 because the ptr_ring is full (NETDEV_TX_BUSY), nothing
ever wakes it again: the poller draining queue 1 wakes queue 0 instead.
veth implements no ndo_tx_timeout, so the netdev watchdog does not kick
in either, and the queue stays stopped indefinitely.

Derive the index from the position of the rq within priv->rq instead,
which is correct regardless of whether XDP was ever enabled.

Scripts to reproduce the stall are available at
https://github.com/netoptimizer/veth-backpressure-performance-testing

## References
- https://git.kernel.org/stable/c/60db47f02bfa2aa688938aa199117ec4f8e31d23
- https://git.kernel.org/stable/c/73f8dd22b1e533a99ecc3f9b5de6c6daccaecace
- https://git.kernel.org/stable/c/90bb11fb29d3c55a2c46dc7c386d096b286e7fcf
- https://git.kernel.org/stable/c/b662a1fb4f3a5ea19bac24eea8315b1d05be51e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74742.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74742
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
