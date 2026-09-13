# [H] netlink: annotate lockless accesses to nlk->max_recvmsg_len

## Summary
Severity: High
Advisory: CVE-2023-53824
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2023-53824
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.218, >=5.11.0 <5.15.160, >=5.16.0 <6.1.24, >=6.2.0 <6.2.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

netlink: annotate lockless accesses to nlk->max_recvmsg_len

syzbot reported a data-race in data-race in netlink_recvmsg() [1]

Indeed, netlink_recvmsg() can be run concurrently,
and netlink_dump() also needs protection.

[1]
BUG: KCSAN: data-race in netlink_recvmsg / netlink_recvmsg

read to 0xffff888141840b38 of 8 bytes by task 23057 on cpu 0:
netlink_recvmsg+0xea/0x730 net/netlink/af_netlink.c:1988
sock_recvmsg_nosec net/socket.c:1017 [inline]
sock_recvmsg net/socket.c:1038 [inline]
__sys_recvfrom+0x1ee/0x2e0 net/socket.c:2194
__do_sys_recvfrom net/socket.c:2212 [inline]
__se_sys_recvfrom net/socket.c:2208 [inline]
__x64_sys_recvfrom+0x78/0x90 net/socket.c:2208
do_syscall_x64 arch/x86/entry/common.c:50 [inline]
do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
entry_SYSCALL_64_after_hwframe+0x63/0xcd

write to 0xffff888141840b38 of 8 bytes by task 23037 on cpu 1:
netlink_recvmsg+0x114/0x730 net/netlink/af_netlink.c:1989
sock_recvmsg_nosec net/socket.c:1017 [inline]
sock_recvmsg net/socket.c:1038 [inline]
____sys_recvmsg+0x156/0x310 net/socket.c:2720
___sys_recvmsg net/socket.c:2762 [inline]
do_recvmmsg+0x2e5/0x710 net/socket.c:2856
__sys_recvmmsg net/socket.c:2935 [inline]
__do_sys_recvmmsg net/socket.c:2958 [inline]
__se_sys_recvmmsg net/socket.c:2951 [inline]
__x64_sys_recvmmsg+0xe2/0x160 net/socket.c:2951
do_syscall_x64 arch/x86/entry/common.c:50 [inline]
do_syscall_64+0x41/0xc0 arch/x86/entry/common.c:80
entry_SYSCALL_64_after_hwframe+0x63/0xcd

value changed: 0x0000000000000000 -> 0x0000000000001000

Reported by Kernel Concurrency Sanitizer on:
CPU: 1 PID: 23037 Comm: syz-executor.2 Not tainted 6.3.0-rc4-syzkaller-00195-g5a57b48fdfcb #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 03/02/2023

## References
- https://git.kernel.org/stable/c/05c9e3fc93b02d18c3ab258d43350a6d44b40bbd
- https://git.kernel.org/stable/c/7cff4103be7c402ecc3e7bf8f95a64089e3c91b8
- https://git.kernel.org/stable/c/a1865f2e7d10dde00d35a2122b38d2e469ae67ed
- https://git.kernel.org/stable/c/e3bcf2a77060bea4d8d09cb09d92c7056f07df5a
- https://git.kernel.org/stable/c/fc4ba13013ddaea8b11b88fd52b35449e2d9cf85
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53824.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53824
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
