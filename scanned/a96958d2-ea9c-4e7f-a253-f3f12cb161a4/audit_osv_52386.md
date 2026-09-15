# [H] CVE-2021-47394

## Summary
Severity: High
Advisory: CVE-2021-47394
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47394
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: unlink table before deleting it

syzbot reports following UAF:
BUG: KASAN: use-after-free in memcmp+0x18f/0x1c0 lib/string.c:955
 nla_strcmp+0xf2/0x130 lib/nlattr.c:836
 nft_table_lookup.part.0+0x1a2/0x460 net/netfilter/nf_tables_api.c:570
 nft_table_lookup net/netfilter/nf_tables_api.c:4064 [inline]
 nf_tables_getset+0x1b3/0x860 net/netfilter/nf_tables_api.c:4064
 nfnetlink_rcv_msg+0x659/0x13f0 net/netfilter/nfnetlink.c:285
 netlink_rcv_skb+0x153/0x420 net/netlink/af_netlink.c:2504

Problem is that all get operations are lockless, so the commit_mutex
held by nft_rcv_nl_event() isn't enough to stop a parallel GET request
from doing read-accesses to the table object even after synchronize_rcu().

To avoid this, unlink the table first and store the table objects in
on-stack scratch space.

## References
- https://git.kernel.org/stable/c/a499b03bf36b0c2e3b958a381d828678ab0ffc5e
- https://git.kernel.org/stable/c/f65c73d3aabb87d4353e0bc4a718b5ae8c43fd04
