# [H] tcp: properly terminate timers for kernel sockets

## Summary
Severity: High
Advisory: CVE-2024-35910
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35910
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.19.312, >=4.20.0 <5.4.274, >=5.5.0 <5.10.215, >=5.11.0 <5.15.154, >=5.16.0 <6.1.85, >=6.2.0 <6.6.26, >=6.7.0 <6.8.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: properly terminate timers for kernel sockets

We had various syzbot reports about tcp timers firing after
the corresponding netns has been dismantled.

Fortunately Josef Bacik could trigger the issue more often,
and could test a patch I wrote two years ago.

When TCP sockets are closed, we call inet_csk_clear_xmit_timers()
to 'stop' the timers.

inet_csk_clear_xmit_timers() can be called from any context,
including when socket lock is held.
This is the reason it uses sk_stop_timer(), aka del_timer().
This means that ongoing timers might finish much later.

For user sockets, this is fine because each running timer
holds a reference on the socket, and the user socket holds
a reference on the netns.

For kernel sockets, we risk that the netns is freed before
timer can complete, because kernel sockets do not hold
reference on the netns.

This patch adds inet_csk_clear_xmit_timers_sync() function
that using sk_stop_timer_sync() to make sure all timers
are terminated before the kernel socket is released.
Modules using kernel sockets close them in their netns exit()
handler.

Also add sock_not_owned_by_me() helper to get LOCKDEP
support : inet_csk_clear_xmit_timers_sync() must not be called
while socket lock is held.

It is very possible we can revert in the future commit
3a58f13a881e ("net: rds: acquire refcount on TCP sockets")
which attempted to solve the issue in rds only.
(net/smc/af_smc.c and net/mptcp/subflow.c have similar code)

We probably can remove the check_net() tests from
tcp_out_of_resources() and __tcp_close() in the future.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-398330.html
- https://git.kernel.org/stable/c/151c9c724d05d5b0dd8acd3e11cb69ef1f2dbada
- https://git.kernel.org/stable/c/2e43d8eba6edd1cf05a3a20fdd77688fa7ec16a4
- https://git.kernel.org/stable/c/44e62f5d35678686734afd47c6a421ad30772e7f
- https://git.kernel.org/stable/c/899265c1389fe022802aae73dbf13ee08837a35a
- https://git.kernel.org/stable/c/91b243de910a9ac8476d40238ab3dbfeedd5b7de
- https://git.kernel.org/stable/c/93f0133b9d589cc6e865f254ad9be3e9d8133f50
- https://git.kernel.org/stable/c/c1ae4d1e76eacddaacb958b67cd942082f800c87
- https://git.kernel.org/stable/c/e3e27d2b446deb1f643758a0c4731f5c22492810
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35910.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
