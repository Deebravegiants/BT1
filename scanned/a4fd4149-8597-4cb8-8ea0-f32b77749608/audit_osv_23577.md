# [M] wireguard: socket: free skb in send6 when ipv6 is disabled

## Summary
Severity: Medium
Advisory: CVE-2022-49153
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49153
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wireguard: socket: free skb in send6 when ipv6 is disabled

I got a memory leak report:

unreferenced object 0xffff8881191fc040 (size 232):
  comm "kworker/u17:0", pid 23193, jiffies 4295238848 (age 3464.870s)
  hex dump (first 32 bytes):
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
    00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
  backtrace:
    [<ffffffff814c3ef4>] slab_post_alloc_hook+0x84/0x3b0
    [<ffffffff814c8977>] kmem_cache_alloc_node+0x167/0x340
    [<ffffffff832974fb>] __alloc_skb+0x1db/0x200
    [<ffffffff82612b5d>] wg_socket_send_buffer_to_peer+0x3d/0xc0
    [<ffffffff8260e94a>] wg_packet_send_handshake_initiation+0xfa/0x110
    [<ffffffff8260ec81>] wg_packet_handshake_send_worker+0x21/0x30
    [<ffffffff8119c558>] process_one_work+0x2e8/0x770
    [<ffffffff8119ca2a>] worker_thread+0x4a/0x4b0
    [<ffffffff811a88e0>] kthread+0x120/0x160
    [<ffffffff8100242f>] ret_from_fork+0x1f/0x30

In function wg_socket_send_buffer_as_reply_to_skb() or wg_socket_send_
buffer_to_peer(), the semantics of send6() is required to free skb. But
when CONFIG_IPV6 is disable, kfree_skb() is missing. This patch adds it
to fix this bug.

## References
- https://git.kernel.org/stable/c/096f9d35cac0a0c95ffafc00db84786b665a4837
- https://git.kernel.org/stable/c/0b19bcb753dbfb74710d12bb2761ec5ed706c726
- https://git.kernel.org/stable/c/402991a9771587acc2947cf6c4d689c5397f2258
- https://git.kernel.org/stable/c/bbbf962d9460194993ee1943a793a0a0af4a7fbf
- https://git.kernel.org/stable/c/ebcc492f4ba14bae54b898f1016a37b4282558d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49153.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49153
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
