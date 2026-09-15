# [H] mptcp: use the workqueue to destroy unaccepted sockets

## Summary
Severity: High
Advisory: CVE-2023-53072
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-02
Source: https://osv.dev/vulnerability/CVE-2023-53072
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <6.1.22, >=6.2.0 <6.2.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: use the workqueue to destroy unaccepted sockets

Christoph reported a UaF at token lookup time after having
refactored the passive socket initialization part:

  BUG: KASAN: use-after-free in __token_bucket_busy+0x253/0x260
  Read of size 4 at addr ffff88810698d5b0 by task syz-executor653/3198

  CPU: 1 PID: 3198 Comm: syz-executor653 Not tainted 6.2.0-rc59af4eaa31c1f6c00c8f1e448ed99a45c66340dd5 #6
  Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS rel-1.13.0-0-gf21b5a4aeb02-prebuilt.qemu.org 04/01/2014
  Call Trace:
   <TASK>
   dump_stack_lvl+0x6e/0x91
   print_report+0x16a/0x46f
   kasan_report+0xad/0x130
   __token_bucket_busy+0x253/0x260
   mptcp_token_new_connect+0x13d/0x490
   mptcp_connect+0x4ed/0x860
   __inet_stream_connect+0x80e/0xd90
   tcp_sendmsg_fastopen+0x3ce/0x710
   mptcp_sendmsg+0xff1/0x1a20
   inet_sendmsg+0x11d/0x140
   __sys_sendto+0x405/0x490
   __x64_sys_sendto+0xdc/0x1b0
   do_syscall_64+0x3b/0x90
   entry_SYSCALL_64_after_hwframe+0x72/0xdc

We need to properly clean-up all the paired MPTCP-level
resources and be sure to release the msk last, even when
the unaccepted subflow is destroyed by the TCP internals
via inet_child_forget().

We can re-use the existing MPTCP_WORK_CLOSE_SUBFLOW infra,
explicitly checking that for the critical scenario: the
closed subflow is the MPC one, the msk is not accepted and
eventually going through full cleanup.

With such change, __mptcp_destroy_sock() is always called
on msk sockets, even on accepted ones. We don't need anymore
to transiently drop one sk reference at msk clone time.

Please note this commit depends on the parent one:

  mptcp: refactor passive socket initialization

## References
- https://git.kernel.org/stable/c/2827f099b3fb9a59263c997400e9182f5d423e84
- https://git.kernel.org/stable/c/804cf487fb0031f3c74755b78d8663333f0ba636
- https://git.kernel.org/stable/c/b6985b9b82954caa53f862d6059d06c0526254f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53072.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53072
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
