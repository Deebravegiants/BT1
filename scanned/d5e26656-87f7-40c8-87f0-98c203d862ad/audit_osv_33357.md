# [H] tcp: Don't call reqsk_fastopen_remove() in tcp_conn_request().

## Summary
Severity: High
Advisory: CVE-2025-40186
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-12
Source: https://osv.dev/vulnerability/CVE-2025-40186
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.157, >=6.2.0 <6.6.113, >=6.7.0 <6.12.54, >=6.13.0 <6.17.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: Don't call reqsk_fastopen_remove() in tcp_conn_request().

syzbot reported the splat below in tcp_conn_request(). [0]

If a listener is close()d while a TFO socket is being processed in
tcp_conn_request(), inet_csk_reqsk_queue_add() does not set reqsk->sk
and calls inet_child_forget(), which calls tcp_disconnect() for the
TFO socket.

After the cited commit, tcp_disconnect() calls reqsk_fastopen_remove(),
where reqsk_put() is called due to !reqsk->sk.

Then, reqsk_fastopen_remove() in tcp_conn_request() decrements the
last req->rsk_refcnt and frees reqsk, and __reqsk_free() at the
drop_and_free label causes the refcount underflow for the listener
and double-free of the reqsk.

Let's remove reqsk_fastopen_remove() in tcp_conn_request().

Note that other callers make sure tp->fastopen_rsk is not NULL.

[0]:
refcount_t: underflow; use-after-free.
WARNING: CPU: 12 PID: 5563 at lib/refcount.c:28 refcount_warn_saturate (lib/refcount.c:28)
Modules linked in:
CPU: 12 UID: 0 PID: 5563 Comm: syz-executor Not tainted syzkaller #0 PREEMPT(full)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 07/12/2025
RIP: 0010:refcount_warn_saturate (lib/refcount.c:28)
Code: ab e8 8e b4 98 ff 0f 0b c3 cc cc cc cc cc 80 3d a4 e4 d6 01 00 75 9c c6 05 9b e4 d6 01 01 48 c7 c7 e8 df fb ab e8 6a b4 98 ff <0f> 0b e9 03 5b 76 00 cc 80 3d 7d e4 d6 01 00 0f 85 74 ff ff ff c6
RSP: 0018:ffffa79fc0304a98 EFLAGS: 00010246
RAX: d83af4db1c6b3900 RBX: ffff9f65c7a69020 RCX: d83af4db1c6b3900
RDX: 0000000000000000 RSI: 00000000ffff7fff RDI: ffffffffac78a280
RBP: 000000009d781b60 R08: 0000000000007fff R09: ffffffffac6ca280
R10: 0000000000017ffd R11: 0000000000000004 R12: ffff9f65c7b4f100
R13: ffff9f65c7d23c00 R14: ffff9f65c7d26000 R15: ffff9f65c7a64ef8
FS:  00007f9f962176c0(0000) GS:ffff9f65fcf00000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 0000200000000180 CR3: 000000000dbbe006 CR4: 0000000000372ef0
Call Trace:
 <IRQ>
 tcp_conn_request (./include/linux/refcount.h:400 ./include/linux/refcount.h:432 ./include/linux/refcount.h:450 ./include/net/sock.h:1965 ./include/net/request_sock.h:131 net/ipv4/tcp_input.c:7301)
 tcp_rcv_state_process (net/ipv4/tcp_input.c:6708)
 tcp_v6_do_rcv (net/ipv6/tcp_ipv6.c:1670)
 tcp_v6_rcv (net/ipv6/tcp_ipv6.c:1906)
 ip6_protocol_deliver_rcu (net/ipv6/ip6_input.c:438)
 ip6_input (net/ipv6/ip6_input.c:500)
 ipv6_rcv (net/ipv6/ip6_input.c:311)
 __netif_receive_skb (net/core/dev.c:6104)
 process_backlog (net/core/dev.c:6456)
 __napi_poll (net/core/dev.c:7506)
 net_rx_action (net/core/dev.c:7569 net/core/dev.c:7696)
 handle_softirqs (kernel/softirq.c:579)
 do_softirq (kernel/softirq.c:480)
 </IRQ>

## References
- https://git.kernel.org/stable/c/2e7cbbbe3d61c63606994b7ff73c72537afe2e1c
- https://git.kernel.org/stable/c/422c1c173c39bbbae1e0eaaf8aefe40b2596233b
- https://git.kernel.org/stable/c/643a94b0cf767325e953591c212be2eb826b9d7f
- https://git.kernel.org/stable/c/64dc47a13aa3d9daf7cec29b44dca8e22a6aea15
- https://git.kernel.org/stable/c/c11ace909e873118295e9eb22dc8c58b0b50eb32
- https://git.kernel.org/stable/c/e359b742eac1eac75cff4e38ee2e8cea492acd9b
- https://git.kernel.org/stable/c/eb85ad5f23268d64b037bfb545cbcba3752f90c7
- https://git.kernel.org/stable/c/ff6a8883f96a5bc74241ce5b3d431a6dcfa2124d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40186.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40186
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
