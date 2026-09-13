# [H] netfilter: nfnetlink_queue: make hash table per queue

## Summary
Severity: High
Advisory: CVE-2026-43084
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43084
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.75 <6.12.83, >=6.18.14 <6.18.24, >=6.19.4 <6.19.14

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nfnetlink_queue: make hash table per queue

Sharing a global hash table among all queues is tempting, but
it can cause crash:

BUG: KASAN: slab-use-after-free in nfqnl_recv_verdict+0x11ac/0x15e0 [nfnetlink_queue]
[..]
 nfqnl_recv_verdict+0x11ac/0x15e0 [nfnetlink_queue]
 nfnetlink_rcv_msg+0x46a/0x930
 kmem_cache_alloc_node_noprof+0x11e/0x450

struct nf_queue_entry is freed via kfree, but parallel cpu can still
encounter such an nf_queue_entry when walking the list.

Alternative fix is to free the nf_queue_entry via kfree_rcu() instead,
but as we have to alloc/free for each skb this will cause more mem
pressure.

## References
- https://git.kernel.org/stable/c/22730cb96093b5be0609063bbb1923dbecd61252
- https://git.kernel.org/stable/c/41e3652a178cb0eecd48e0e6e27fbb73a004046a
- https://git.kernel.org/stable/c/936206e3f6ff411581e615e930263d6f8b78df9d
- https://git.kernel.org/stable/c/9e5ebef91120d2764aefe557c3a484b6288f341f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43084.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43084
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
