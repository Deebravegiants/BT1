# [H] netfilter: nf_tables: always release netdev hooks from notifier

## Summary
Severity: High
Advisory: CVE-2023-54200
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-30
Source: https://osv.dev/vulnerability/CVE-2023-54200
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_tables: always release netdev hooks from notifier

This reverts "netfilter: nf_tables: skip netdev events generated on netns removal".

The problem is that when a veth device is released, the veth release
callback will also queue the peer netns device for removal.

Its possible that the peer netns is also slated for removal.  In this
case, the device memory is already released before the pre_exit hook of
the peer netns runs:

BUG: KASAN: slab-use-after-free in nf_hook_entry_head+0x1b8/0x1d0
Read of size 8 at addr ffff88812c0124f0 by task kworker/u8:1/45
Workqueue: netns cleanup_net
Call Trace:
 nf_hook_entry_head+0x1b8/0x1d0
 __nf_unregister_net_hook+0x76/0x510
 nft_netdev_unregister_hooks+0xa0/0x220
 __nft_release_hook+0x184/0x490
 nf_tables_pre_exit_net+0x12f/0x1b0
 ..

Order is:
1. First netns is released, veth_dellink() queues peer netns device
   for removal
2. peer netns is queued for removal
3. peer netns device is released, unreg event is triggered
4. unreg event is ignored because netns is going down
5. pre_exit hook calls nft_netdev_unregister_hooks but device memory
   might be free'd already.

## References
- https://git.kernel.org/stable/c/30e4b13b1bfbdf3bf3b27036d8209ea1b9f0d880
- https://git.kernel.org/stable/c/8d56f00c61f67b450fbbdcb874855e60ad92c560
- https://git.kernel.org/stable/c/94032527efbac13be702c76afb9d872c0cca7a43
- https://git.kernel.org/stable/c/dc1c9fd4a8bbe1e06add9053010b652449bfe411
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/54xxx/CVE-2023-54200.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-54200
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
