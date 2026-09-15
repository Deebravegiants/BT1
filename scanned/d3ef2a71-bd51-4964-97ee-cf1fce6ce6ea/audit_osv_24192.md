# [M] net: sched: fix memory leak in tcindex_set_parms

## Summary
Severity: Medium
Advisory: CVE-2022-50396
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50396
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <4.14.308, >=4.15.0 <4.19.276, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.19, >=6.1.0 <6.1.5, >=6.2.0 <6.2.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: sched: fix memory leak in tcindex_set_parms

Syzkaller reports a memory leak as follows:
====================================
BUG: memory leak
unreferenced object 0xffff88810c287f00 (size 256):
  comm "syz-executor105", pid 3600, jiffies 4294943292 (age 12.990s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<ffffffff814cf9f0>] kmalloc_trace+0x20/0x90 mm/slab_common.c:1046
    [<ffffffff839c9e07>] kmalloc include/linux/slab.h:576 [inline]
    [<ffffffff839c9e07>] kmalloc_array include/linux/slab.h:627 [inline]
    [<ffffffff839c9e07>] kcalloc include/linux/slab.h:659 [inline]
    [<ffffffff839c9e07>] tcf_exts_init include/net/pkt_cls.h:250 [inline]
    [<ffffffff839c9e07>] tcindex_set_parms+0xa7/0xbe0 net/sched/cls_tcindex.c:342
    [<ffffffff839caa1f>] tcindex_change+0xdf/0x120 net/sched/cls_tcindex.c:553
    [<ffffffff8394db62>] tc_new_tfilter+0x4f2/0x1100 net/sched/cls_api.c:2147
    [<ffffffff8389e91c>] rtnetlink_rcv_msg+0x4dc/0x5d0 net/core/rtnetlink.c:6082
    [<ffffffff839eba67>] netlink_rcv_skb+0x87/0x1d0 net/netlink/af_netlink.c:2540
    [<ffffffff839eab87>] netlink_unicast_kernel net/netlink/af_netlink.c:1319 [inline]
    [<ffffffff839eab87>] netlink_unicast+0x397/0x4c0 net/netlink/af_netlink.c:1345
    [<ffffffff839eb046>] netlink_sendmsg+0x396/0x710 net/netlink/af_netlink.c:1921
    [<ffffffff8383e796>] sock_sendmsg_nosec net/socket.c:714 [inline]
    [<ffffffff8383e796>] sock_sendmsg+0x56/0x80 net/socket.c:734
    [<ffffffff8383eb08>] ____sys_sendmsg+0x178/0x410 net/socket.c:2482
    [<ffffffff83843678>] ___sys_sendmsg+0xa8/0x110 net/socket.c:2536
    [<ffffffff838439c5>] __sys_sendmmsg+0x105/0x330 net/socket.c:2622
    [<ffffffff83843c14>] __do_sys_sendmmsg net/socket.c:2651 [inline]
    [<ffffffff83843c14>] __se_sys_sendmmsg net/socket.c:2648 [inline]
    [<ffffffff83843c14>] __x64_sys_sendmmsg+0x24/0x30 net/socket.c:2648
    [<ffffffff84605fd5>] do_syscall_x64 arch/x86/entry/common.c:50 [inline]
    [<ffffffff84605fd5>] do_syscall_64+0x35/0xb0 arch/x86/entry/common.c:80
    [<ffffffff84800087>] entry_SYSCALL_64_after_hwframe+0x63/0xcd
====================================

Kernel uses tcindex_change() to change an existing
filter properties.

Yet the problem is that, during the process of changing,
if `old_r` is retrieved from `p->perfect`, then
kernel uses tcindex_alloc_perfect_hash() to newly
allocate filter results, uses tcindex_filter_result_init()
to clear the old filter result, without destroying
its tcf_exts structure, which triggers the above memory leak.

To be more specific, there are only two source for the `old_r`,
according to the tcindex_lookup(). `old_r` is retrieved from
`p->perfect`, or `old_r` is retrieved from `p->h`.

  * If `old_r` is retrieved from `p->perfect`, kernel uses
tcindex_alloc_perfect_hash() to newly allocate the
filter results. Then `r` is assigned with `cp->perfect + handle`,
which is newly allocated. So condition `old_r && old_r != r` is
true in this situation, and kernel uses tcindex_filter_result_init()
to clear the old filter result, without destroying
its tcf_exts structure

  * If `old_r` is retrieved from `p->h`, then `p->perfect` is NULL
according to the tcindex_lookup(). Considering that `cp->h`
is directly copied from `p->h` and `p->perfect` is NULL,
`r` is assigned with `tcindex_lookup(cp, handle)`, whose value
should be the same as `old_r`, so condition `old_r && old_r != r`
is false in this situation, kernel ignores using
tcindex_filter_result_init() to clear the old filter result.

So only when `old_r` is retrieved from `p->perfect` does kernel use
tcindex_filter_result_init() to clear the old filter result, which
triggers the above memory leak.

Considering that there already exists a tc_filter_wq workqueue
to destroy the old tcindex_d
---truncated---

## References
- https://git.kernel.org/stable/c/01d0d2b8b4e3cf2110baba9371c0c3d04ad5c77b
- https://git.kernel.org/stable/c/18c3fa7a7fdbb4d21dafc8a7710ae2c1680930f6
- https://git.kernel.org/stable/c/372ae77cf11d11fb118cbe2d37def9dd5f826abd
- https://git.kernel.org/stable/c/399ab7fe0fa0d846881685fd4e57e9a8ef7559f7
- https://git.kernel.org/stable/c/3abebc503a5148072052c229c6b04b329a420ecd
- https://git.kernel.org/stable/c/53af9c793f644d5841d84d8e0ad83bd7ab47f3e0
- https://git.kernel.org/stable/c/55ac68b53f1cea1926ee2313afc5d66b91daad71
- https://git.kernel.org/stable/c/6c55953e232ea668731091d111066521f3b7719b
- https://git.kernel.org/stable/c/7a6fb69bbcb21e9ce13bdf18c008c268874f0480
- https://git.kernel.org/stable/c/7c183dc0af472dec33d2c0786a5e356baa8cad19
- https://git.kernel.org/stable/c/b314f6c3512108d7a656c5caf07c82d1bbbdc0f1
- https://git.kernel.org/stable/c/c4de6057e7c6654983acb63d939d26ac0d7bbf39
- https://git.kernel.org/stable/c/facc4405e8b7407e03216207b1d1d640127de0c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50396.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
