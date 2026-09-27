# [H] net: qualcomm: rmnet: fix endpoint use-after-free in rmnet_dellink()

## Summary
Severity: High
Advisory: CVE-2026-64188
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-64188
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.260, >=5.11.0 <5.15.211, >=5.16.0 <6.1.177, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.37, >=6.19.0 <7.0.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: qualcomm: rmnet: fix endpoint use-after-free in rmnet_dellink()

rmnet_dellink() removes the endpoint from the hash table with
hlist_del_init_rcu() and then immediately frees it with kfree(). However,
RCU readers on the receive path (rmnet_rx_handler ->
__rmnet_map_ingress_handler) may still hold a reference to the endpoint and
dereference ep->egress_dev after the memory has been freed. The endpoint is
a kmalloc-32 object, and the stale read at offset 8 corresponds to the
egress_dev pointer.

  BUG: unable to handle page fault for address: ffffffffde942eef
  Oops: 0002 [#1] SMP NOPTI
  CPU: 1 UID: 0 PID: 137 Comm: poc_write Not tainted 7.0.0+ #4 PREEMPTLAZY
  RIP: 0010:rmnet_vnd_rx_fixup (rmnet_vnd.c:27)
  Call Trace:
   <TASK>
   __rmnet_map_ingress_handler (rmnet_handlers.c:48 rmnet_handlers.c:101)
   rmnet_rx_handler (rmnet_handlers.c:129 rmnet_handlers.c:235)
   __netif_receive_skb_core.constprop.0 (net/core/dev.c:6096)
   __netif_receive_skb_one_core (net/core/dev.c:6208)
   netif_receive_skb (net/core/dev.c:6467)
   tun_get_user (drivers/net/tun.c:1955)
   tun_chr_write_iter (drivers/net/tun.c:2003)
   vfs_write (fs/read_write.c:688)
   ksys_write (fs/read_write.c:740)
   </TASK>

Add an rcu_head field to struct rmnet_endpoint and replace kfree() with
kfree_rcu() so the endpoint memory remains valid through the RCU grace
period. Also remove the rmnet_vnd_dellink() call and inline only the
nr_rmnet_devs decrement, since rmnet_vnd_dellink() would set
ep->egress_dev to NULL during the grace period, creating a data race
with lockless readers.

## References
- https://git.kernel.org/stable/c/1078ae8175777e80c9637996fb4a46c55f0ce576
- https://git.kernel.org/stable/c/310b93246bfec7d4452507e0c15477377ed9f025
- https://git.kernel.org/stable/c/41e06fcc5df0774d212e70c5b503fc769492bce3
- https://git.kernel.org/stable/c/8b17adf6d4fb6bf61fa4c3f58366a7c082799a71
- https://git.kernel.org/stable/c/9918698cf3aee4032e12bb42fd5a951dc465339b
- https://git.kernel.org/stable/c/c4e676c3505c5058922dc1a6f1ded795f6758135
- https://git.kernel.org/stable/c/d00c953a8f69921f484b629801766da68f27f658
- https://git.kernel.org/stable/c/f193e38cb257d033060b63f1cfd94af076b3a2ab
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64188.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64188
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
