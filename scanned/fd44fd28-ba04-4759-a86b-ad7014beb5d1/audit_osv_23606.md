# [M] bpf, sockmap: Fix memleak in tcp_bpf_sendmsg while sk msg is full

## Summary
Severity: Medium
Advisory: CVE-2022-49209
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49209
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.4.189, >=5.5.0 <5.10.110, >=5.11.0 <5.15.33, >=5.16.0 <5.16.19, >=5.17.0 <5.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf, sockmap: Fix memleak in tcp_bpf_sendmsg while sk msg is full

If tcp_bpf_sendmsg() is running while sk msg is full. When sk_msg_alloc()
returns -ENOMEM error, tcp_bpf_sendmsg() goes to wait_for_memory. If partial
memory has been alloced by sk_msg_alloc(), that is, msg_tx->sg.size is
greater than osize after sk_msg_alloc(), memleak occurs. To fix we use
sk_msg_trim() to release the allocated memory, then goto wait for memory.

Other call paths of sk_msg_alloc() have the similar issue, such as
tls_sw_sendmsg(), so handle sk_msg_trim logic inside sk_msg_alloc(),
as Cong Wang suggested.

This issue can cause the following info:
WARNING: CPU: 3 PID: 7950 at net/core/stream.c:208 sk_stream_kill_queues+0xd4/0x1a0
Call Trace:
 <TASK>
 inet_csk_destroy_sock+0x55/0x110
 __tcp_close+0x279/0x470
 tcp_close+0x1f/0x60
 inet_release+0x3f/0x80
 __sock_release+0x3d/0xb0
 sock_close+0x11/0x20
 __fput+0x92/0x250
 task_work_run+0x6a/0xa0
 do_exit+0x33b/0xb60
 do_group_exit+0x2f/0xa0
 get_signal+0xb6/0x950
 arch_do_signal_or_restart+0xac/0x2a0
 exit_to_user_mode_prepare+0xa9/0x200
 syscall_exit_to_user_mode+0x12/0x30
 do_syscall_64+0x46/0x80
 entry_SYSCALL_64_after_hwframe+0x44/0xae
 </TASK>

WARNING: CPU: 3 PID: 2094 at net/ipv4/af_inet.c:155 inet_sock_destruct+0x13c/0x260
Call Trace:
 <TASK>
 __sk_destruct+0x24/0x1f0
 sk_psock_destroy+0x19b/0x1c0
 process_one_work+0x1b3/0x3c0
 kthread+0xe6/0x110
 ret_from_fork+0x22/0x30
 </TASK>

## References
- https://git.kernel.org/stable/c/6d03722c34d9603df325f67c6d30dc1b7b3c6067
- https://git.kernel.org/stable/c/9c34e38c4a870eb30b13f42f5b44f42e9d19ccb8
- https://git.kernel.org/stable/c/bec34a91eba3483e1830c02bdd36f8f968642047
- https://git.kernel.org/stable/c/d0b85dfc6f01d26808e2576c6537c131b590e270
- https://git.kernel.org/stable/c/de3a8d8fab0710186f7864ec812836d8d70da3c9
- https://git.kernel.org/stable/c/f677328f05f52d535cbdc15cb04476db49477eb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49209.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49209
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
