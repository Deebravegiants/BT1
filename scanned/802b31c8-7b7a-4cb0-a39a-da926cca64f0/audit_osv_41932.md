# [H] vsock/vmci: fix UAF when peer resets connection during handshake

## Summary
Severity: High
Advisory: CVE-2026-64115
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64115
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.9.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/vmci: fix UAF when peer resets connection during handshake

vmci_transport_recv_connecting_server() returned err = 0 for a peer
RST in its default switch arm:

	err = pkt->type == VMCI_TRANSPORT_PACKET_TYPE_RST ? 0 : -EINVAL;

That made vmci_transport_recv_listen() skip vsock_remove_pending(),
leaving the pending socket on the listener's pending_links with
sk_state = TCP_CLOSE while destroy: still dropped the explicit
reference taken before schedule_delayed_work().

One second later vsock_pending_work() observed is_pending=true and
performed full cleanup: vsock_remove_pending() then the two trailing
sock_put(sk) calls -- the first reached refcount 0 and __sk_freed
the socket, and the second wrote into the freed object:

  BUG: KASAN: slab-use-after-free in refcount_warn_saturate
  Write of size 4 at addr ffff88800b1cac80 by task kworker
  Workqueue: events vsock_pending_work

Treat peer RST like any other unexpected packet type (err = -EINVAL).
All destroy: arms now return err < 0, so vmci_transport_recv_listen()
removes pending from pending_links synchronously and
vsock_pending_work() takes the is_pending=false / !rejected branch,
dropping only its own work reference.  This also closes the
multi-packet race Sashiko reported on v2: pending is removed from
the list before any subsequent packet can find it.

The pre-existing sk_acceptq_removed() gap on the err < 0 path of
vmci_transport_recv_listen() that Sashiko also noted is not
introduced or changed by this patch.

Tested on lts-6.12.79 with KASAN: 52/100 unpatched -> 0/100 patched.

## References
- https://git.kernel.org/stable/c/1dd531e28f61edd286edc486ab068f135b5ae1eb
- https://git.kernel.org/stable/c/1e19f08552b90070ed18bafb1763c78297823af6
- https://git.kernel.org/stable/c/440447699c681e26ed58e9c309cad718270a18b4
- https://git.kernel.org/stable/c/47e63077605c6c2aa45b3df9847a8cdc1f1f6ef9
- https://git.kernel.org/stable/c/99e22ddf4edb63dc8382bc028af928056d3450cf
- https://git.kernel.org/stable/c/9fe74e42914c851d68069713b7b917a9c33faf26
- https://git.kernel.org/stable/c/cc27e989a5dfdfcfc1cca7c3be27a0c7532b46cb
- https://git.kernel.org/stable/c/ecda37f8faab3220da199335e42564cb7a9ad145
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64115.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64115
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
