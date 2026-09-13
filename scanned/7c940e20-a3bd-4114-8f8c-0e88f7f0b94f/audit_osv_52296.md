# [M] CVE-2021-47297

## Summary
Severity: Medium
Advisory: CVE-2021-47297
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47297
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: fix uninit-value in caif_seqpkt_sendmsg

When nr_segs equal to zero in iovec_from_user, the object
msg->msg_iter.iov is uninit stack memory in caif_seqpkt_sendmsg
which is defined in ___sys_sendmsg. So we cann't just judge
msg->msg_iter.iov->base directlly. We can use nr_segs to judge
msg in caif_seqpkt_sendmsg whether has data buffers.

=====================================================
BUG: KMSAN: uninit-value in caif_seqpkt_sendmsg+0x693/0xf60 net/caif/caif_socket.c:542
Call Trace:
 __dump_stack lib/dump_stack.c:77 [inline]
 dump_stack+0x1c9/0x220 lib/dump_stack.c:118
 kmsan_report+0xf7/0x1e0 mm/kmsan/kmsan_report.c:118
 __msan_warning+0x58/0xa0 mm/kmsan/kmsan_instr.c:215
 caif_seqpkt_sendmsg+0x693/0xf60 net/caif/caif_socket.c:542
 sock_sendmsg_nosec net/socket.c:652 [inline]
 sock_sendmsg net/socket.c:672 [inline]
 ____sys_sendmsg+0x12b6/0x1350 net/socket.c:2343
 ___sys_sendmsg net/socket.c:2397 [inline]
 __sys_sendmmsg+0x808/0xc90 net/socket.c:2480
 __compat_sys_sendmmsg net/compat.c:656 [inline]

## References
- https://git.kernel.org/stable/c/d4c7797ab1517515f0d08b3bc1c6b48883889c54
- https://git.kernel.org/stable/c/d9d646acad2c3590e189bb5d5c86ab8bd8a2dfc3
- https://git.kernel.org/stable/c/ffe31dd70b70a40cd6b21b78c1713a23e021843a
- https://git.kernel.org/stable/c/1582a02fecffcee306663035a295e28e1c4aaaff
- https://git.kernel.org/stable/c/452c3ed7bf63721b07bc2238ed1261bb26027e85
- https://git.kernel.org/stable/c/5c6d8e2f7187b8e45a18c27acb7a3885f03ee3db
- https://git.kernel.org/stable/c/9413c0abb57f70a953b1116318d6aa478013c35d
- https://git.kernel.org/stable/c/991e634360f2622a683b48dfe44fe6d9cb765a09
