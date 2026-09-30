# [C] Revert "smb: client: fix TCP timers deadlock after rmmod"

## Summary
Severity: Critical
Advisory: CVE-2025-22077
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22077
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

Revert "smb: client: fix TCP timers deadlock after rmmod"

This reverts commit e9f2517a3e18a54a3943c098d2226b245d488801.

Commit e9f2517a3e18 ("smb: client: fix TCP timers deadlock after
rmmod") is intended to fix a null-ptr-deref in LOCKDEP, which is
mentioned as CVE-2024-54680, but is actually did not fix anything;
The issue can be reproduced on top of it. [0]

Also, it reverted the change by commit ef7134c7fc48 ("smb: client:
Fix use-after-free of network namespace.") and introduced a real
issue by reviving the kernel TCP socket.

When a reconnect happens for a CIFS connection, the socket state
transitions to FIN_WAIT_1.  Then, inet_csk_clear_xmit_timers_sync()
in tcp_close() stops all timers for the socket.

If an incoming FIN packet is lost, the socket will stay at FIN_WAIT_1
forever, and such sockets could be leaked up to net.ipv4.tcp_max_orphans.

Usually, FIN can be retransmitted by the peer, but if the peer aborts
the connection, the issue comes into reality.

I warned about this privately by pointing out the exact report [1],
but the bogus fix was finally merged.

So, we should not stop the timers to finally kill the connection on
our side in that case, meaning we must not use a kernel socket for
TCP whose sk->sk_net_refcnt is 0.

The kernel socket does not have a reference to its netns to make it
possible to tear down netns without cleaning up every resource in it.

For example, tunnel devices use a UDP socket internally, but we can
destroy netns without removing such devices and let it complete
during exit.  Otherwise, netns would be leaked when the last application
died.

However, this is problematic for TCP sockets because TCP has timers to
close the connection gracefully even after the socket is close()d.  The
lifetime of the socket and its netns is different from the lifetime of
the underlying connection.

If the socket user does not maintain the netns lifetime, the timer could
be fired after the socket is close()d and its netns is freed up, resulting
in use-after-free.

Actually, we have seen so many similar issues and converted such sockets
to have a reference to netns.

That's why I converted the CIFS client socket to have a reference to
netns (sk->sk_net_refcnt == 1), which is somehow mentioned as out-of-scope
of CIFS and technically wrong in e9f2517a3e18, but **is in-scope and right
fix**.

Regarding the LOCKDEP issue, we can prevent the module unload by
bumping the module refcount when switching the LOCKDDEP key in
sock_lock_init_class_and_name(). [2]

For a while, let's revert the bogus fix.

Note that now we can use sk_net_refcnt_upgrade() for the socket
conversion, but I'll do so later separately to make backport easy.

## References
- https://git.kernel.org/stable/c/4b6f6bf1bde8d6045c389fda8d21c304dfe49384
- https://git.kernel.org/stable/c/8dbf060480236877703bff0106fc984576184d11
- https://git.kernel.org/stable/c/95d2b9f693ff2a1180a23d7d59acc0c4e72f4c41
- https://git.kernel.org/stable/c/f761eeefd531e6550cd3a5c047835b4892acb00d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22077.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22077
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
