# [H] sctp: add mutual exclusion in proc_sctp_do_udp_port()

## Summary
Severity: High
Advisory: CVE-2025-22062
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22062
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.11.0 <5.15.184, >=5.16.0 <6.1.140, >=6.2.0 <6.6.92, >=6.7.0 <6.12.23, >=6.13.0 <6.13.11, >=6.14.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

sctp: add mutual exclusion in proc_sctp_do_udp_port()

We must serialize calls to sctp_udp_sock_stop() and sctp_udp_sock_start()
or risk a crash as syzbot reported:

Oops: general protection fault, probably for non-canonical address 0xdffffc000000000d: 0000 [#1] SMP KASAN PTI
KASAN: null-ptr-deref in range [0x0000000000000068-0x000000000000006f]
CPU: 1 UID: 0 PID: 6551 Comm: syz.1.44 Not tainted 6.14.0-syzkaller-g7f2ff7b62617 #0 PREEMPT(full)
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 02/12/2025
 RIP: 0010:kernel_sock_shutdown+0x47/0x70 net/socket.c:3653
Call Trace:
 <TASK>
  udp_tunnel_sock_release+0x68/0x80 net/ipv4/udp_tunnel_core.c:181
  sctp_udp_sock_stop+0x71/0x160 net/sctp/protocol.c:930
  proc_sctp_do_udp_port+0x264/0x450 net/sctp/sysctl.c:553
  proc_sys_call_handler+0x3d0/0x5b0 fs/proc/proc_sysctl.c:601
  iter_file_splice_write+0x91c/0x1150 fs/splice.c:738
  do_splice_from fs/splice.c:935 [inline]
  direct_splice_actor+0x18f/0x6c0 fs/splice.c:1158
  splice_direct_to_actor+0x342/0xa30 fs/splice.c:1102
  do_splice_direct_actor fs/splice.c:1201 [inline]
  do_splice_direct+0x174/0x240 fs/splice.c:1227
  do_sendfile+0xafd/0xe50 fs/read_write.c:1368
  __do_sys_sendfile64 fs/read_write.c:1429 [inline]
  __se_sys_sendfile64 fs/read_write.c:1415 [inline]
  __x64_sys_sendfile64+0x1d8/0x220 fs/read_write.c:1415
  do_syscall_x64 arch/x86/entry/syscall_64.c:63 [inline]

## References
- https://git.kernel.org/stable/c/10206302af856791fbcc27a33ed3c3eb09b2793d
- https://git.kernel.org/stable/c/386507cb6fb7cdef598ddcb3f0fa37e6ca9e789d
- https://git.kernel.org/stable/c/65ccb2793da7401772a3ffe85355c831b313c59f
- https://git.kernel.org/stable/c/b3598f53211ba1025485306de2733bdd241311a3
- https://git.kernel.org/stable/c/d3d7675d77622f6ca1aae14c51f80027b36283f8
- https://git.kernel.org/stable/c/e5178bfc55b3a78000f0f8298e7ade88783ce581
- https://git.kernel.org/stable/c/efb8cb487be8f4ba6aaef616011d702d6a083ed1
- https://lists.debian.org/debian-lts-announce/2025/08/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22062.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22062
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
