# [C] tipc: clear sock->sk on the failed-insert path in tipc_sk_create()

## Summary
Severity: Critical
Advisory: CVE-2026-68117
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68117
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=5.19.0 <6.6.148, >=6.2.0 <6.12.101, >=6.7.0 <6.18.42, >=6.13.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tipc: clear sock->sk on the failed-insert path in tipc_sk_create()

When tipc_sk_create() fails to insert the new socket (tipc_sk_insert()
returns non-zero), its error path frees the sk with sk_free() but leaves
sock->sk pointing at the freed object:

	if (tipc_sk_insert(tsk)) {
		sk_free(sk);
		pr_warn("Socket create failed; port number exhausted\n");
		return -EINVAL;
	}

This is harmless for plain socket(): the syscall layer clears sock->ops
before releasing, so tipc_release() is never called. It is not harmless
on the accept() path. tipc_accept() creates the pre-allocated child
socket with tipc_sk_create(net, new_sock, 0, kern); on failure it leaves
new_sock->sk dangling and new_sock->ops non-NULL, and do_accept() then
fput()s the new file, so __sock_release() -> tipc_release() runs
lock_sock(new_sock->sk) on the freed sk -- a use-after-free write of the
sk_lock spinlock.

tipc_release() already guards this exact "failed accept() releases a
pre-allocated child" case with "if (sk == NULL) return 0;", but the
guard is bypassed because tipc_sk_create() left sock->sk non-NULL
(dangling) rather than NULL.

Clear sock->sk on the failed-insert path so the existing tipc_release()
NULL check fires and the use-after-free is avoided.

The tipc_sk_insert() failure is reached when the per-netns socket
rhashtable hits its max_size (tsk_rht_params.max_size = 1048576, ~2M
elements) -- i.e. once a netns holds ~2M TIPC sockets every insert
returns -E2BIG.

  BUG: KASAN: slab-use-after-free in lock_sock_nested (net/core/sock.c:3839)
  Write of size 8 at addr ffff8880047cdc38 by task init/1
   lock_sock_nested (net/core/sock.c:3839)
   tipc_release (net/tipc/socket.c:638)
   __sock_release (net/socket.c:710)
   sock_close (net/socket.c:1501)
   __fput (fs/file_table.c:512)
  Allocated by task 1:
   sk_alloc (net/core/sock.c:2308)
   tipc_sk_create (net/tipc/socket.c:487)
   tipc_accept (net/tipc/socket.c:2744)
   do_accept (net/socket.c:2034)
  Freed by task 1:
   __sk_destruct (net/core/sock.c:2391)
   tipc_sk_create (net/tipc/socket.c:504)
   tipc_accept (net/tipc/socket.c:2744)
   do_accept (net/socket.c:2034)

## References
- https://git.kernel.org/stable/c/5f5a41a48dbf9eda57b67ce23e548602cf7195a6
- https://git.kernel.org/stable/c/82f59aa27f33bd014a7d8739371ab5712d15e33b
- https://git.kernel.org/stable/c/8d6f26d48e61ef34f1921289401dbf36b10816af
- https://git.kernel.org/stable/c/b07d87b31631edb6529e6cdcca790a7489d1250d
- https://git.kernel.org/stable/c/ba0533fc163f905fe817cfabdf8ed4058da44800
- https://git.kernel.org/stable/c/dd29891ed840f6b8d020b759d0dc4a00b1d6e4ea
- https://git.kernel.org/stable/c/efebc23e9b29e3e5a9e2127dd066929f7f0d315e
- https://git.kernel.org/stable/c/f9596b1566616a8be0592dbceccb6344a7c6f6bb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
