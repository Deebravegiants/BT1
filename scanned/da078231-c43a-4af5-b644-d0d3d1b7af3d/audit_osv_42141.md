# [H] xfrm: fix sk_dst_cache double-free in xfrm_user_policy()

## Summary
Severity: High
Advisory: CVE-2026-64581
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-64581
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.14.0 <5.10.267, >=5.11.0 <5.15.218, >=5.16.0 <6.1.185, >=6.2.0 <6.6.154, >=6.7.0 <6.12.106, >=6.13.0 <6.18.47, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: fix sk_dst_cache double-free in xfrm_user_policy()

xfrm_user_policy() clears the socket dst cache with __sk_dst_reset(),
i.e. the non-atomic __sk_dst_set(sk, NULL): it reads sk_dst_cache with
rcu_dereference_protected(), stores NULL and dst_release()s the old dst.
That is only safe if no other thread modifies sk_dst_cache concurrently.

For a connected UDP socket that does not hold: the transmit fast path
(udp_sendmsg -> sk_dst_check -> sk_dst_reset) resets the cache locklessly
with an atomic xchg(). A per-socket policy change racing a send can make
both sides observe the same old dst and each dst_release() it, dropping
the socket's single reference twice and freeing the xfrm_dst bundle while
it is still referenced:

  BUG: KASAN: slab-use-after-free in dst_release
  Write of size 4 at addr ffff88801897b6c0 by task exploit/155
  Call Trace:
   ...
   dst_release (... ./include/linux/rcuref.h:109)
   xfrm_user_policy (./include/net/sock.h:2239 ./include/net/sock.h:2256 net/xfrm/xfrm_state.c:3053)
   do_ip_setsockopt (net/ipv4/ip_sockglue.c:1347)
   ip_setsockopt (net/ipv4/ip_sockglue.c:1417)
   do_sock_setsockopt (net/socket.c:2368)
   __sys_setsockopt (net/socket.c:2393)
   __x64_sys_setsockopt (net/socket.c:2396)
   do_syscall_64 (arch/x86/entry/syscall_64.c:94)
   entry_SYSCALL_64_after_hwframe (arch/x86/entry/entry_64.S:121)

Reachable by an unprivileged user via a user+network namespace.

Use the atomic sk_dst_reset() so the cache is cleared and released with a
single xchg(): whichever side wins releases the dst once, the other sees
NULL and does nothing. Behaviour is otherwise unchanged.

## References
- https://git.kernel.org/stable/c/0ea8f06454012d9e7f9c6e6253df710949bf6294
- https://git.kernel.org/stable/c/8dd8929b71c4f06c614f8f54c2cc070453faae16
- https://git.kernel.org/stable/c/96b678d08268b5f5c6fc99d4289d9b7e334fc683
- https://git.kernel.org/stable/c/a9340ebdc13f8bb5063c0bc0b037ee7e640d4ae9
- https://git.kernel.org/stable/c/c283e9ada7fcb7dd4b10592623086b2e6d2f9925
- https://git.kernel.org/stable/c/e8686fd8d18b99f3a9038683045b2f2338a7706d
- https://git.kernel.org/stable/c/f0ab9a71167bae308e05ab13b65e2007504a603f
- https://git.kernel.org/stable/c/f833821e4b52ab6335d443ede5fb79c38e61d19a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64581.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
