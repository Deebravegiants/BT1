# [H] netfilter: ctnetlink: fix use-after-free in ctnetlink_dump_exp_ct()

## Summary
Severity: High
Advisory: CVE-2026-23458
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23458
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: ctnetlink: fix use-after-free in ctnetlink_dump_exp_ct()

ctnetlink_dump_exp_ct() stores a conntrack pointer in cb->data for the
netlink dump callback ctnetlink_exp_ct_dump_table(), but drops the
conntrack reference immediately after netlink_dump_start().  When the
dump spans multiple rounds, the second recvmsg() triggers the dump
callback which dereferences the now-freed conntrack via nfct_help(ct),
leading to a use-after-free on ct->ext.

The bug is that the netlink_dump_control has no .start or .done
callbacks to manage the conntrack reference across dump rounds.  Other
dump functions in the same file (e.g. ctnetlink_get_conntrack) properly
use .start/.done callbacks for this purpose.

Fix this by adding .start and .done callbacks that hold and release the
conntrack reference for the duration of the dump, and move the
nfct_help() call after the cb->args[0] early-return check in the dump
callback to avoid dereferencing ct->ext unnecessarily.

 BUG: KASAN: slab-use-after-free in ctnetlink_exp_ct_dump_table+0x4f/0x2e0
 Read of size 8 at addr ffff88810597ebf0 by task ctnetlink_poc/133

 CPU: 1 UID: 0 PID: 133 Comm: ctnetlink_poc Not tainted 7.0.0-rc2+ #3 PREEMPTLAZY
 Call Trace:
  <TASK>
  ctnetlink_exp_ct_dump_table+0x4f/0x2e0
  netlink_dump+0x333/0x880
  netlink_recvmsg+0x3e2/0x4b0
  ? aa_sk_perm+0x184/0x450
  sock_recvmsg+0xde/0xf0

 Allocated by task 133:
  kmem_cache_alloc_noprof+0x134/0x440
  __nf_conntrack_alloc+0xa8/0x2b0
  ctnetlink_create_conntrack+0xa1/0x900
  ctnetlink_new_conntrack+0x3cf/0x7d0
  nfnetlink_rcv_msg+0x48e/0x510
  netlink_rcv_skb+0xc9/0x1f0
  nfnetlink_rcv+0xdb/0x220
  netlink_unicast+0x3ec/0x590
  netlink_sendmsg+0x397/0x690
  __sys_sendmsg+0xf4/0x180

 Freed by task 0:
  slab_free_after_rcu_debug+0xad/0x1e0
  rcu_core+0x5c3/0x9c0

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/04c8907ce4e3d3e26c5e1a3e47aa5d17082cbb56
- https://git.kernel.org/stable/c/5cb81eeda909dbb2def209dd10636b51549a3f8a
- https://git.kernel.org/stable/c/9821b47f669eb82791fa0b1a6ebaf9aa219bea72
- https://git.kernel.org/stable/c/bdf2724eefd4455a66863abb025bab8d3aa98c57
- https://git.kernel.org/stable/c/cd541f15b60e2257441398cf495d978f816d09f8
- https://git.kernel.org/stable/c/d8cd0efbccc5cfb0a80da744a7da76e1333ab925
- https://git.kernel.org/stable/c/f025171feef2ac65663d7986f1d5ff0c28d6b2a9
- https://git.kernel.org/stable/c/f04cc86d59906513d2d62183b882966fc0ae0390
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23458.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23458
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
