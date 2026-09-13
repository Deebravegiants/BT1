# [H] netfilter: nft_ct: fix use-after-free in timeout object destroy

## Summary
Severity: High
Advisory: CVE-2026-31665
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31665
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.169, >=6.2.0 <6.6.135, >=6.7.0 <6.12.82, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nft_ct: fix use-after-free in timeout object destroy

nft_ct_timeout_obj_destroy() frees the timeout object with kfree()
immediately after nf_ct_untimeout(), without waiting for an RCU grace
period. Concurrent packet processing on other CPUs may still hold
RCU-protected references to the timeout object obtained via
rcu_dereference() in nf_ct_timeout_data().

Add an rcu_head to struct nf_ct_timeout and use kfree_rcu() to defer
freeing until after an RCU grace period, matching the approach already
used in nfnetlink_cttimeout.c.

KASAN report:
 BUG: KASAN: slab-use-after-free in nf_conntrack_tcp_packet+0x1381/0x29d0
 Read of size 4 at addr ffff8881035fe19c by task exploit/80

 Call Trace:
  nf_conntrack_tcp_packet+0x1381/0x29d0
  nf_conntrack_in+0x612/0x8b0
  nf_hook_slow+0x70/0x100
  __ip_local_out+0x1b2/0x210
  tcp_sendmsg_locked+0x722/0x1580
  __sys_sendto+0x2d8/0x320

 Allocated by task 75:
  nft_ct_timeout_obj_init+0xf6/0x290
  nft_obj_init+0x107/0x1b0
  nf_tables_newobj+0x680/0x9c0
  nfnetlink_rcv_batch+0xc29/0xe00

 Freed by task 26:
  nft_obj_destroy+0x3f/0xa0
  nf_tables_trans_destroy_work+0x51c/0x5c0
  process_one_work+0x2c4/0x5a0

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/070abdf1b04325b21a20a2a0c39a2208af107275
- https://git.kernel.org/stable/c/aa7cfa16f98f8ec3e6d47c34e1a8c1ae4b9b8b77
- https://git.kernel.org/stable/c/b42aca3660dc2627a29a38131597ca610dc451f9
- https://git.kernel.org/stable/c/c458fc1c278a65ad5381083121d39a479973ebed
- https://git.kernel.org/stable/c/c581e5c8f2b59158f62efe61c1a3dc36189081ff
- https://git.kernel.org/stable/c/d0983b48c10d1509fd795c155f8b1e832e1369ff
- https://git.kernel.org/stable/c/f16fe84879a5280f05ebbcea593a189ba0f3e79a
- https://git.kernel.org/stable/c/f8dca15a1b190787bbd03285304b569631160eda
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31665.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31665
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
