# [C] tcp: restore RCU grace period in tcp_ao_destroy_sock

## Summary
Severity: Critical
Advisory: CVE-2026-64459
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64459
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.18.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: restore RCU grace period in tcp_ao_destroy_sock

Commit 51e547e8c89c ("tcp: Free TCP-AO/TCP-MD5 info/keys without RCU")
removed the call_rcu() callback from tcp_ao_destroy_sock(), arguing that
"the destruction of info/keys is delayed until the socket destructor"
and therefore "no one can discover it anymore".

That argument does not hold for the call site in tcp_connect()
(net/ipv4/tcp_output.c:4327-4332). At that point the socket is in
TCP_SYN_SENT, has already been inserted into the inet ehash by
inet_hash_connect() in tcp_v4_connect(), and is therefore very much
discoverable: any softirq running tcp_v4_rcv() on another CPU can take
the socket out of the ehash, walk into tcp_inbound_hash(), and load
tp->ao_info via implicit RCU before bh_lock_sock_nested() is taken on
the destroying CPU.

The reader path then enters __tcp_ao_do_lookup() (net/ipv4/tcp_ao.c:208)
which re-loads tp->ao_info via rcu_dereference_check(); the re-load can
still observe the (about-to-be-freed) pointer because there is no
synchronize_rcu() between rcu_assign_pointer(tp->ao_info, NULL) and
tcp_ao_info_free() in tcp_ao_destroy_sock(). The captured pointer is
then walked at line 223:

	hlist_for_each_entry_rcu(key, &ao->head, node, ...)

The writer's synchronous kfree() is free to complete between the line
218 re-fetch and the line 223 hlist iteration. The slab is reused
(or simply LIST_POISON1-stamped if not yet reused) and the iteration
walks attacker-controlled or poison memory in softirq context.

Reproducer (no debug shim, stock x86_64 v7.1-rc2 SMP+KASAN, QEMU+KVM):
an unprivileged uid=1000 process inside CLONE_NEWUSER|CLONE_NEWNET
installs TCP_MD5SIG + TCP_AO_ADD_KEY on a TCP socket, sprays forged
TCP-AO segments toward its eventual 4-tuple via raw sockets, then
calls connect(). The md5-wins reconciliation in tcp_connect() fires
tcp_ao_destroy_sock(); the softirq backlog reader on the loopback
NAPI path crashes on the freed ao->head.first walk:

  Oops: general protection fault, probably for non-canonical
    address 0xfbd59c000000002f
  KASAN: maybe wild-memory-access in range
    [0xdead000000000178-0xdead00000000017f]
  CPU: 0 UID: 1000 PID: 100 Comm: repro_userns
  RIP: 0010:__tcp_ao_do_lookup+0x107/0x1c0
  Call Trace: <IRQ>
    __tcp_ao_do_lookup+0x107/0x1c0
    tcp_ao_inbound_lookup.constprop.0+0x12a/0x200
    tcp_inbound_ao_hash+0x5ea/0x1520
    tcp_inbound_hash+0x7ce/0x1240
    tcp_v4_rcv+0x1e7a/0x3e10
    ...

Restore the RCU grace period: re-add struct rcu_head to tcp_ao_info
and replace the synchronous tcp_ao_info_free() with a call_rcu()
callback. Readers that captured tp->ao_info before rcu_assign_pointer
NULLed it now see the object remain valid until rcu_read_unlock().
With the patch applied the reproducer runs cleanly for 2000 iterations
on the same kernel build.

## References
- https://git.kernel.org/stable/c/4caf12c778fed3dc3824cf36263be5e2c491fbd0
- https://git.kernel.org/stable/c/657646c08c94ef7b9dbe468fe7828032216f9841
- https://git.kernel.org/stable/c/8bc4d43bccbd60efe85d0a44d5bf41762f2f0c30
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
