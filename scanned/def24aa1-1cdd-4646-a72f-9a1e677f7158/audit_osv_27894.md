# [M] bpf, sockmap: Fix NULL pointer dereference in sk_psock_verdict_data_ready()

## Summary
Severity: Medium
Advisory: CVE-2024-26731
Ecosystem: Linux
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-04-03
Source: https://osv.dev/vulnerability/CVE-2024-26731
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.80, >=6.2.0 <6.6.19, >=6.4.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix NULL pointer dereference in sk_psock_verdict_data_ready()

syzbot reported the following NULL pointer dereference issue [1]:

  BUG: kernel NULL pointer dereference, address: 0000000000000000
  [...]
  RIP: 0010:0x0
  [...]
  Call Trace:
   <TASK>
   sk_psock_verdict_data_ready+0x232/0x340 net/core/skmsg.c:1230
   unix_stream_sendmsg+0x9b4/0x1230 net/unix/af_unix.c:2293
   sock_sendmsg_nosec net/socket.c:730 [inline]
   __sock_sendmsg+0x221/0x270 net/socket.c:745
   ____sys_sendmsg+0x525/0x7d0 net/socket.c:2584
   ___sys_sendmsg net/socket.c:2638 [inline]
   __sys_sendmsg+0x2b0/0x3a0 net/socket.c:2667
   do_syscall_64+0xf9/0x240
   entry_SYSCALL_64_after_hwframe+0x6f/0x77

If sk_psock_verdict_data_ready() and sk_psock_stop_verdict() are called
concurrently, psock->saved_data_ready can be NULL, causing the above issue.

This patch fixes this issue by calling the appropriate data ready function
using the sk_psock_data_ready() helper and protecting it from concurrency
with sk->sk_callback_lock.

## References
- https://git.kernel.org/stable/c/4588b13abcbd561ec67f5b3c1cb2eff690990a54
- https://git.kernel.org/stable/c/4cd12c6065dfcdeba10f49949bffcf383b3952d8
- https://git.kernel.org/stable/c/9b099ed46dcaf1403c531ff02c3d7400fa37fa26
- https://git.kernel.org/stable/c/d61608a4e394f23e0dca099df9eb8e555453d949
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26731.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26731
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
