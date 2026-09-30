# [H] kcm: close race conditions on sk_receive_queue

## Summary
Severity: High
Advisory: CVE-2022-49814
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49814
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.6.0 <4.14.300, >=4.15.0 <4.19.267, >=4.20.0 <5.4.225, >=5.5.0 <5.10.156, >=5.11.0 <5.15.80, >=5.16.0 <6.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

kcm: close race conditions on sk_receive_queue

sk->sk_receive_queue is protected by skb queue lock, but for KCM
sockets its RX path takes mux->rx_lock to protect more than just
skb queue. However, kcm_recvmsg() still only grabs the skb queue
lock, so race conditions still exist.

We can teach kcm_recvmsg() to grab mux->rx_lock too but this would
introduce a potential performance regression as struct kcm_mux can
be shared by multiple KCM sockets.

So we have to enforce skb queue lock in requeue_rx_msgs() and handle
skb peek case carefully in kcm_wait_data(). Fortunately,
skb_recv_datagram() already handles it nicely and is widely used by
other sockets, we can just switch to skb_recv_datagram() after
getting rid of the unnecessary sock lock in kcm_recvmsg() and
kcm_splice_read(). Side note: SOCK_DONE is not used by KCM sockets,
so it is safe to get rid of this check too.

I ran the original syzbot reproducer for 30 min without seeing any
issue.

## References
- https://git.kernel.org/stable/c/22f6b5d47396b4287662668ee3f5c1f766cb4259
- https://git.kernel.org/stable/c/4154b6afa2bd639214ff259d912faad984f7413a
- https://git.kernel.org/stable/c/5121197ecc5db58c07da95eb1ff82b98b121a221
- https://git.kernel.org/stable/c/bf92e54597d842da127c59833b365d6faeeaf020
- https://git.kernel.org/stable/c/ce57d6474ae999a3b2d442314087473a646a65c7
- https://git.kernel.org/stable/c/d9ad4de92e184b19bcae4da10dac0275abf83931
- https://git.kernel.org/stable/c/f7b0e95071bb4be4b811af3f0bfc3e200eedeaa3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49814.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49814
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
