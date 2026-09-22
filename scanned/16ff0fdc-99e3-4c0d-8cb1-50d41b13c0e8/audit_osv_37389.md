# [H] virtio_net: Fix UAF on dst_ops when IFF_XMIT_DST_RELEASE is cleared and napi_tx is false

## Summary
Severity: High
Advisory: CVE-2026-31469
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-31469
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio_net: Fix UAF on dst_ops when IFF_XMIT_DST_RELEASE is cleared and napi_tx is false

A UAF issue occurs when the virtio_net driver is configured with napi_tx=N
and the device's IFF_XMIT_DST_RELEASE flag is cleared
(e.g., during the configuration of tc route filter rules).

When IFF_XMIT_DST_RELEASE is removed from the net_device, the network stack
expects the driver to hold the reference to skb->dst until the packet
is fully transmitted and freed. In virtio_net with napi_tx=N,
skbs may remain in the virtio transmit ring for an extended period.

If the network namespace is destroyed while these skbs are still pending,
the corresponding dst_ops structure has freed. When a subsequent packet
is transmitted, free_old_xmit() is triggered to clean up old skbs.
It then calls dst_release() on the skb associated with the stale dst_entry.
Since the dst_ops (referenced by the dst_entry) has already been freed,
a UAF kernel paging request occurs.

fix it by adds skb_dst_drop(skb) in start_xmit to explicitly release
the dst reference before the skb is queued in virtio_net.

Call Trace:
 Unable to handle kernel paging request at virtual address ffff80007e150000
 CPU: 2 UID: 0 PID: 6236 Comm: ping Kdump: loaded Not tainted 7.0.0-rc1+ #6 PREEMPT
  ...
  percpu_counter_add_batch+0x3c/0x158 lib/percpu_counter.c:98 (P)
  dst_release+0xe0/0x110  net/core/dst.c:177
  skb_release_head_state+0xe8/0x108 net/core/skbuff.c:1177
  sk_skb_reason_drop+0x54/0x2d8 net/core/skbuff.c:1255
  dev_kfree_skb_any_reason+0x64/0x78 net/core/dev.c:3469
  napi_consume_skb+0x1c4/0x3a0 net/core/skbuff.c:1527
  __free_old_xmit+0x164/0x230  drivers/net/virtio_net.c:611 [virtio_net]
  free_old_xmit drivers/net/virtio_net.c:1081 [virtio_net]
  start_xmit+0x7c/0x530 drivers/net/virtio_net.c:3329 [virtio_net]
  ...

Reproduction Steps:
NETDEV="enp3s0"

config_qdisc_route_filter() {
    tc qdisc del dev $NETDEV root
    tc qdisc add dev $NETDEV root handle 1: prio
    tc filter add dev $NETDEV parent 1:0 \
	protocol ip prio 100 route to 100 flowid 1:1
    ip route add 192.168.1.100/32 dev $NETDEV realm 100
}

test_ns() {
    ip netns add testns
    ip link set $NETDEV netns testns
    ip netns exec testns ifconfig $NETDEV  10.0.32.46/24
    ip netns exec testns ping -c 1 10.0.32.1
    ip netns del testns
}

config_qdisc_route_filter

test_ns
sleep 2
test_ns

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/63d45077b97bb0e0fe0c75931acbbca7a47af141
- https://git.kernel.org/stable/c/8a4790850e710fd6771e4d2112168ed1dd6c0e54
- https://git.kernel.org/stable/c/9a18629f2525781f0f3dda7be72b204e4cf77d08
- https://git.kernel.org/stable/c/ba8bda9a0896746053aa97ac6c3e08168729172c
- https://git.kernel.org/stable/c/be0e63f3b97bbaf453c542e8a15ba2a536e2ac01
- https://git.kernel.org/stable/c/c1ec36cb3768574b916f20d2d7415fd14fa1bf12
- https://git.kernel.org/stable/c/f04733c4dc40c43899c3d1c97afbae5831a3770f
- https://git.kernel.org/stable/c/fedd2e1630cac920844997227ccbe7b26a76375a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31469.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31469
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
