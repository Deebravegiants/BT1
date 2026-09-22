# [M] rose: Fix NULL pointer dereference in rose_send_frame()

## Summary
Severity: Medium
Advisory: CVE-2022-49916
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49916
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <4.9.333, >=4.10.0 <4.14.299, >=4.15.0 <4.19.265, >=4.20.0 <5.4.224, >=5.5.0 <5.10.154, >=5.11.0 <5.15.78, >=5.16.0 <6.0.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

rose: Fix NULL pointer dereference in rose_send_frame()

The syzkaller reported an issue:

KASAN: null-ptr-deref in range [0x0000000000000380-0x0000000000000387]
CPU: 0 PID: 4069 Comm: kworker/0:15 Not tainted 6.0.0-syzkaller-02734-g0326074ff465 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/22/2022
Workqueue: rcu_gp srcu_invoke_callbacks
RIP: 0010:rose_send_frame+0x1dd/0x2f0 net/rose/rose_link.c:101
Call Trace:
 <IRQ>
 rose_transmit_clear_request+0x1d5/0x290 net/rose/rose_link.c:255
 rose_rx_call_request+0x4c0/0x1bc0 net/rose/af_rose.c:1009
 rose_loopback_timer+0x19e/0x590 net/rose/rose_loopback.c:111
 call_timer_fn+0x1a0/0x6b0 kernel/time/timer.c:1474
 expire_timers kernel/time/timer.c:1519 [inline]
 __run_timers.part.0+0x674/0xa80 kernel/time/timer.c:1790
 __run_timers kernel/time/timer.c:1768 [inline]
 run_timer_softirq+0xb3/0x1d0 kernel/time/timer.c:1803
 __do_softirq+0x1d0/0x9c8 kernel/softirq.c:571
 [...]
 </IRQ>

It triggers NULL pointer dereference when 'neigh->dev->dev_addr' is
called in the rose_send_frame(). It's the first occurrence of the
`neigh` is in rose_loopback_timer() as `rose_loopback_neigh', and
the 'dev' in 'rose_loopback_neigh' is initialized sa nullptr.

It had been fixed by commit 3b3fd068c56e3fbea30090859216a368398e39bf
("rose: Fix Null pointer dereference in rose_send_frame()") ever.
But it's introduced by commit 3c53cd65dece47dd1f9d3a809f32e59d1d87b2b8
("rose: check NULL rose_loopback_neigh->loopback") again.

We fix it by add NULL check in rose_transmit_clear_request(). When
the 'dev' in 'neigh' is NULL, we don't reply the request and just
clear it.

syzkaller don't provide repro, and I provide a syz repro like:
r0 = syz_init_net_socket$bt_sco(0x1f, 0x5, 0x2)
ioctl$sock_inet_SIOCSIFFLAGS(r0, 0x8914, &(0x7f0000000180)={'rose0\x00', 0x201})
r1 = syz_init_net_socket$rose(0xb, 0x5, 0x0)
bind$rose(r1, &(0x7f00000000c0)=@full={0xb, @dev, @null, 0x0, [@null, @null, @netrom, @netrom, @default, @null]}, 0x40)
connect$rose(r1, &(0x7f0000000240)=@short={0xb, @dev={0xbb, 0xbb, 0xbb, 0x1, 0x0}, @remote={0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0xcc, 0x1}, 0x1, @netrom={0xbb, 0xbb, 0xbb, 0xbb, 0xbb, 0x0, 0x0}}, 0x1c)

## References
- https://git.kernel.org/stable/c/01b9c68c121847d05a4ccef68244dadf82bfa331
- https://git.kernel.org/stable/c/3e2129c67daca21043a26575108f6286c85e71f6
- https://git.kernel.org/stable/c/5b46adfbee1e429f33b10a88d6c00fa88f3d6c77
- https://git.kernel.org/stable/c/a601e5eded33bb88b8a42743db8fef3ad41dd97e
- https://git.kernel.org/stable/c/b13be5e852b03f376058027e462fad4230240891
- https://git.kernel.org/stable/c/bbc03d74e641e824754443b908454ca9e203773e
- https://git.kernel.org/stable/c/e97c089d7a49f67027395ddf70bf327eeac2611e
- https://git.kernel.org/stable/c/f06186e5271b980bac03f5c97276ed0146ddc9b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49916.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49916
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
