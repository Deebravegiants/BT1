# [H] net/smc: fix warning in smc_rx_splice() when calling get_page()

## Summary
Severity: High
Advisory: CVE-2025-40012
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-20
Source: https://osv.dev/vulnerability/CVE-2025-40012
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.50, >=6.13.0 <6.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/smc: fix warning in smc_rx_splice() when calling get_page()

smc_lo_register_dmb() allocates DMB buffers with kzalloc(), which are
later passed to get_page() in smc_rx_splice(). Since kmalloc memory is
not page-backed, this triggers WARN_ON_ONCE() in get_page() and prevents
holding a refcount on the buffer. This can lead to use-after-free if
the memory is released before splice_to_pipe() completes.

Use folio_alloc() instead, ensuring DMBs are page-backed and safe for
get_page().

WARNING: CPU: 18 PID: 12152 at ./include/linux/mm.h:1330 smc_rx_splice+0xaf8/0xe20 [smc]
CPU: 18 UID: 0 PID: 12152 Comm: smcapp Kdump: loaded Not tainted 6.17.0-rc3-11705-g9cf4672ecfee #10 NONE
Hardware name: IBM 3931 A01 704 (z/VM 7.4.0)
Krnl PSW : 0704e00180000000 000793161032696c (smc_rx_splice+0xafc/0xe20 [smc])
           R:0 T:1 IO:1 EX:1 Key:0 M:1 W:0 P:0 AS:3 CC:2 PM:0 RI:0 EA:3
Krnl GPRS: 0000000000000000 001cee80007d3001 00077400000000f8 0000000000000005
           0000000000000001 001cee80007d3006 0007740000001000 001c000000000000
           000000009b0c99e0 0000000000001000 001c0000000000f8 001c000000000000
           000003ffcc6f7c88 0007740003e98000 0007931600000005 000792969b2ff7b8
Krnl Code: 0007931610326960: af000000		mc	0,0
           0007931610326964: a7f4ff43		brc	15,00079316103267ea
          #0007931610326968: af000000		mc	0,0
          >000793161032696c: a7f4ff3f		brc	15,00079316103267ea
           0007931610326970: e320f1000004	lg	%r2,256(%r15)
           0007931610326976: c0e53fd1b5f5	brasl	%r14,000793168fd5d560
           000793161032697c: a7f4fbb5		brc	15,00079316103260e6
           0007931610326980: b904002b		lgr	%r2,%r11
Call Trace:
 smc_rx_splice+0xafc/0xe20 [smc]
 smc_rx_splice+0x756/0xe20 [smc])
 smc_rx_recvmsg+0xa74/0xe00 [smc]
 smc_splice_read+0x1ce/0x3b0 [smc]
 sock_splice_read+0xa2/0xf0
 do_splice_read+0x198/0x240
 splice_file_to_pipe+0x7e/0x110
 do_splice+0x59e/0xde0
 __do_splice+0x11a/0x2d0
 __s390x_sys_splice+0x140/0x1f0
 __do_syscall+0x122/0x280
 system_call+0x6e/0x90
Last Breaking-Event-Address:
smc_rx_splice+0x960/0xe20 [smc]
---[ end trace 0000000000000000 ]---

## References
- https://git.kernel.org/stable/c/14fc4fdae42e34d7ee871b292ac2ecc61c2c5de7
- https://git.kernel.org/stable/c/a35c04de2565db191726b5741e6b66a35002c652
- https://git.kernel.org/stable/c/d5411685dc2f6ac7bdf01a0a204d56cae38c6cf6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40012.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40012
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
