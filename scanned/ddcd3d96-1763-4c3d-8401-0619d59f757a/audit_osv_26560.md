# [M] rxrpc: Fix potential data race in rxrpc_wait_to_be_connected()

## Summary
Severity: Medium
Advisory: CVE-2023-53345
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53345
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.2.16, >=6.3.0 <6.3.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: Fix potential data race in rxrpc_wait_to_be_connected()

Inside the loop in rxrpc_wait_to_be_connected() it checks call->error to
see if it should exit the loop without first checking the call state.  This
is probably safe as if call->error is set, the call is dead anyway, but we
should probably wait for the call state to have been set to completion
first, lest it cause surprise on the way out.

Fix this by only accessing call->error if the call is complete.  We don't
actually need to access the error inside the loop as we'll do that after.

This caused the following report:

    BUG: KCSAN: data-race in rxrpc_send_data / rxrpc_set_call_completion

    write to 0xffff888159cf3c50 of 4 bytes by task 25673 on cpu 1:
     rxrpc_set_call_completion+0x71/0x1c0 net/rxrpc/call_state.c:22
     rxrpc_send_data_packet+0xba9/0x1650 net/rxrpc/output.c:479
     rxrpc_transmit_one+0x1e/0x130 net/rxrpc/output.c:714
     rxrpc_decant_prepared_tx net/rxrpc/call_event.c:326 [inline]
     rxrpc_transmit_some_data+0x496/0x600 net/rxrpc/call_event.c:350
     rxrpc_input_call_event+0x564/0x1220 net/rxrpc/call_event.c:464
     rxrpc_io_thread+0x307/0x1d80 net/rxrpc/io_thread.c:461
     kthread+0x1ac/0x1e0 kernel/kthread.c:376
     ret_from_fork+0x1f/0x30 arch/x86/entry/entry_64.S:308

    read to 0xffff888159cf3c50 of 4 bytes by task 25672 on cpu 0:
     rxrpc_send_data+0x29e/0x1950 net/rxrpc/sendmsg.c:296
     rxrpc_do_sendmsg+0xb7a/0xc20 net/rxrpc/sendmsg.c:726
     rxrpc_sendmsg+0x413/0x520 net/rxrpc/af_rxrpc.c:565
     sock_sendmsg_nosec net/socket.c:724 [inline]
     sock_sendmsg net/socket.c:747 [inline]
     ____sys_sendmsg+0x375/0x4c0 net/socket.c:2501
     ___sys_sendmsg net/socket.c:2555 [inline]
     __sys_sendmmsg+0x263/0x500 net/socket.c:2641
     __do_sys_sendmmsg net/socket.c:2670 [inline]
     __se_sys_sendmmsg net/socket.c:2667 [inline]
     __x64_sys_sendmmsg+0x57/0x60 net/socket.c:2667
     do_syscall_x64 arch/x86/entry/common.c:50 [inline]
     do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
     entry_SYSCALL_64_after_hwframe+0x63/0xcd

    value changed: 0x00000000 -> 0xffffffea

## References
- https://git.kernel.org/stable/c/2b5fdc0f5caa505afe34d608e2eefadadf2ee67a
- https://git.kernel.org/stable/c/3e8ba61a3fe4475a9b5c9fbfc664435c6795d872
- https://git.kernel.org/stable/c/454e48a9ff04c5fa1631bb172070fcb6389b97f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53345.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53345
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
