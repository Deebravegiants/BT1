# [H] rxrpc: Fix locking in rxrpc's sendmsg

## Summary
Severity: High
Advisory: CVE-2022-49998
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49998
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.140, >=5.11.0 <5.15.64, >=5.16.0 <5.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix locking in rxrpc's sendmsg

Fix three bugs in the rxrpc's sendmsg implementation:

 (1) rxrpc_new_client_call() should release the socket lock when returning
     an error from rxrpc_get_call_slot().

 (2) rxrpc_wait_for_tx_window_intr() will return without the call mutex
     held in the event that we're interrupted by a signal whilst waiting
     for tx space on the socket or relocking the call mutex afterwards.

     Fix this by: (a) moving the unlock/lock of the call mutex up to
     rxrpc_send_data() such that the lock is not held around all of
     rxrpc_wait_for_tx_window*() and (b) indicating to higher callers
     whether we're return with the lock dropped.  Note that this means
     recvmsg() will not block on this call whilst we're waiting.

 (3) After dropping and regaining the call mutex, rxrpc_send_data() needs
     to go and recheck the state of the tx_pending buffer and the
     tx_total_len check in case we raced with another sendmsg() on the same
     call.

Thinking on this some more, it might make sense to have different locks for
sendmsg() and recvmsg().  There's probably no need to make recvmsg() wait
for sendmsg().  It does mean that recvmsg() can return MSG_EOR indicating
that a call is dead before a sendmsg() to that call returns - but that can
currently happen anyway.

Without fix (2), something like the following can be induced:

	WARNING: bad unlock balance detected!
	5.16.0-rc6-syzkaller #0 Not tainted
	-------------------------------------
	syz-executor011/3597 is trying to release lock (&call->user_mutex) at:
	[<ffffffff885163a3>] rxrpc_do_sendmsg+0xc13/0x1350 net/rxrpc/sendmsg.c:748
	but there are no more locks to release!

	other info that might help us debug this:
	no locks held by syz-executor011/3597.
	...
	Call Trace:
	 <TASK>
	 __dump_stack lib/dump_stack.c:88 [inline]
	 dump_stack_lvl+0xcd/0x134 lib/dump_stack.c:106
	 print_unlock_imbalance_bug include/trace/events/lock.h:58 [inline]
	 __lock_release kernel/locking/lockdep.c:5306 [inline]
	 lock_release.cold+0x49/0x4e kernel/locking/lockdep.c:5657
	 __mutex_unlock_slowpath+0x99/0x5e0 kernel/locking/mutex.c:900
	 rxrpc_do_sendmsg+0xc13/0x1350 net/rxrpc/sendmsg.c:748
	 rxrpc_sendmsg+0x420/0x630 net/rxrpc/af_rxrpc.c:561
	 sock_sendmsg_nosec net/socket.c:704 [inline]
	 sock_sendmsg+0xcf/0x120 net/socket.c:724
	 ____sys_sendmsg+0x6e8/0x810 net/socket.c:2409
	 ___sys_sendmsg+0xf3/0x170 net/socket.c:2463
	 __sys_sendmsg+0xe5/0x1b0 net/socket.c:2492
	 do_syscall_x64 arch/x86/entry/common.c:50 [inline]
	 do_syscall_64+0x35/0xb0 arch/x86/entry/common.c:80
	 entry_SYSCALL_64_after_hwframe+0x44/0xae

[Thanks to Hawkins Jiawei and Khalid Masum for their attempts to fix this]

## References
- https://git.kernel.org/stable/c/091dc91e119fdd61432347231724f4e861c6b465
- https://git.kernel.org/stable/c/2bc769b8edb158be7379d15f36e23d66cf850053
- https://git.kernel.org/stable/c/79e2ca7aa96e80961828ab6312264633b66183cc
- https://git.kernel.org/stable/c/b0f571ecd7943423c25947439045f0d352ca3dbf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49998.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49998
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
