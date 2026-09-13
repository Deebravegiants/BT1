# [H] CVE-2021-46992

## Summary
Severity: High
Advisory: CVE-2021-46992
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46992
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nftables: avoid overflows in nft_hash_buckets()

Number of buckets being stored in 32bit variables, we have to
ensure that no overflows occur in nft_hash_buckets()

syzbot injected a size == 0x40000000 and reported:

UBSAN: shift-out-of-bounds in ./include/linux/log2.h:57:13
shift exponent 64 is too large for 64-bit type 'long unsigned int'
CPU: 1 PID: 29539 Comm: syz-executor.4 Not tainted 5.12.0-rc7-syzkaller #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 01/01/2011
Call Trace:
 __dump_stack lib/dump_stack.c:79 [inline]
 dump_stack+0x141/0x1d7 lib/dump_stack.c:120
 ubsan_epilogue+0xb/0x5a lib/ubsan.c:148
 __ubsan_handle_shift_out_of_bounds.cold+0xb1/0x181 lib/ubsan.c:327
 __roundup_pow_of_two include/linux/log2.h:57 [inline]
 nft_hash_buckets net/netfilter/nft_set_hash.c:411 [inline]
 nft_hash_estimate.cold+0x19/0x1e net/netfilter/nft_set_hash.c:652
 nft_select_set_ops net/netfilter/nf_tables_api.c:3586 [inline]
 nf_tables_newset+0xe62/0x3110 net/netfilter/nf_tables_api.c:4322
 nfnetlink_rcv_batch+0xa09/0x24b0 net/netfilter/nfnetlink.c:488
 nfnetlink_rcv_skb_batch net/netfilter/nfnetlink.c:612 [inline]
 nfnetlink_rcv+0x3af/0x420 net/netfilter/nfnetlink.c:630
 netlink_unicast_kernel net/netlink/af_netlink.c:1312 [inline]
 netlink_unicast+0x533/0x7d0 net/netlink/af_netlink.c:1338
 netlink_sendmsg+0x856/0xd90 net/netlink/af_netlink.c:1927
 sock_sendmsg_nosec net/socket.c:654 [inline]
 sock_sendmsg+0xcf/0x120 net/socket.c:674
 ____sys_sendmsg+0x6e8/0x810 net/socket.c:2350
 ___sys_sendmsg+0xf3/0x170 net/socket.c:2404
 __sys_sendmsg+0xe5/0x1b0 net/socket.c:2433
 do_syscall_64+0x2d/0x70 arch/x86/entry/common.c:46

## References
- https://git.kernel.org/stable/c/a54754ec9891830ba548e2010c889e3c8146e449
- https://git.kernel.org/stable/c/c77e2ef18167ad334e27610ced9a7f6af5ec1787
- https://git.kernel.org/stable/c/efcd730ddd6f25578bd31bfe703e593e2421d708
- https://git.kernel.org/stable/c/1e8ab479cfbe5751efccedb95afb9b112a5ba475
- https://git.kernel.org/stable/c/2824cafc6a93792d9ad85939c499161214d84c4b
- https://git.kernel.org/stable/c/72b49dd116ca00a46a11d5a4d8d7987f05ed9cd7
- https://git.kernel.org/stable/c/a388d10961ff8578b1a6691945d406c0f33aa71b
