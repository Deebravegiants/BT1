# [H] net, bpf: check master for NULL in xdp_master_redirect()

## Summary
Severity: High
Advisory: CVE-2026-64545
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-64545
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net, bpf: check master for NULL in xdp_master_redirect()

xdp_master_redirect() dereferences the result of
netdev_master_upper_dev_get_rcu() without a NULL check, but that helper
returns NULL when the receiving device has no upper-master adjacency.

The reach guard only checks netif_is_bond_slave(). On bond slave release
bond_upper_dev_unlink() drops the upper-master adjacency before clearing
IFF_SLAVE, so an XDP_TX reaching xdp_master_redirect() in that window
still passes netif_is_bond_slave() while master is already NULL, and
faults on master->flags at offset 0xb0:

  BUG: kernel NULL pointer dereference, address: 00000000000000b0
  RIP: 0010:xdp_master_redirect (net/core/filter.c:4432)
  Call Trace:
   xdp_master_redirect (net/core/filter.c:4432)
   bpf_prog_run_generic_xdp (include/net/xdp.h:700)
   do_xdp_generic (net/core/dev.c:5608)
   __netif_receive_skb_one_core (net/core/dev.c:6204)
   process_backlog (net/core/dev.c:6319)
   __napi_poll (net/core/dev.c:7729)
   net_rx_action (net/core/dev.c:7792)
   handle_softirqs (kernel/softirq.c:622)
   __dev_queue_xmit (include/linux/bottom_half.h:33)
   packet_sendmsg (net/packet/af_packet.c:3082)
   __sys_sendto (net/socket.c:2252)
  Kernel panic - not syncing: Fatal exception in interrupt

The missing check dates back to the original code; commit 1921f91298d1
("net, bpf: fix null-ptr-deref in xdp_master_redirect() for down master")
later added the master->flags read where the fault now lands but kept the
unconditional deref. Check master for NULL before use; a NULL master is
treated the same as one that is not up.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://git.kernel.org/stable/c/03b743586a2469744e96e9c1015096d07240935d
- https://git.kernel.org/stable/c/3876318ea54e83eb70982b8280a3c5e4e32269bf
- https://git.kernel.org/stable/c/4edbcacca09f92b85d3951b6add11894b20a84bc
- https://git.kernel.org/stable/c/89c103d702b25ceb2d097faf854deb47b53b17ff
- https://git.kernel.org/stable/c/c99ca049e910d61ddbd28cc2c47242f2bfbb4970
- https://git.kernel.org/stable/c/e2a56441233131fe18a76001de347ecda217e40c
- https://git.kernel.org/stable/c/e82d8cc4321c373dc46e741cd2dfdaa7921fddb7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64545.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64545
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
