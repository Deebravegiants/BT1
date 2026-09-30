# [M] nbd: always initialize struct msghdr completely

## Summary
Severity: Medium
Advisory: CVE-2024-26638
Ecosystem: Linux
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-18
Source: https://osv.dev/vulnerability/CVE-2024-26638
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.76, >=6.2.0 <6.6.15, >=6.7.0 <6.7.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

nbd: always initialize struct msghdr completely

syzbot complains that msg->msg_get_inq value can be uninitialized [1]

struct msghdr got many new fields recently, we should always make
sure their values is zero by default.

[1]
 BUG: KMSAN: uninit-value in tcp_recvmsg+0x686/0xac0 net/ipv4/tcp.c:2571
  tcp_recvmsg+0x686/0xac0 net/ipv4/tcp.c:2571
  inet_recvmsg+0x131/0x580 net/ipv4/af_inet.c:879
  sock_recvmsg_nosec net/socket.c:1044 [inline]
  sock_recvmsg+0x12b/0x1e0 net/socket.c:1066
  __sock_xmit+0x236/0x5c0 drivers/block/nbd.c:538
  nbd_read_reply drivers/block/nbd.c:732 [inline]
  recv_work+0x262/0x3100 drivers/block/nbd.c:863
  process_one_work kernel/workqueue.c:2627 [inline]
  process_scheduled_works+0x104e/0x1e70 kernel/workqueue.c:2700
  worker_thread+0xf45/0x1490 kernel/workqueue.c:2781
  kthread+0x3ed/0x540 kernel/kthread.c:388
  ret_from_fork+0x66/0x80 arch/x86/kernel/process.c:147
  ret_from_fork_asm+0x11/0x20 arch/x86/entry/entry_64.S:242

Local variable msg created at:
  __sock_xmit+0x4c/0x5c0 drivers/block/nbd.c:513
  nbd_read_reply drivers/block/nbd.c:732 [inline]
  recv_work+0x262/0x3100 drivers/block/nbd.c:863

CPU: 1 PID: 7465 Comm: kworker/u5:1 Not tainted 6.7.0-rc7-syzkaller-00041-gf016f7547aee #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 11/17/2023
Workqueue: nbd5-recv recv_work

## References
- https://git.kernel.org/stable/c/1960f2b534da1e6c65fb96f9e98bda773495f406
- https://git.kernel.org/stable/c/78fbb92af27d0982634116c7a31065f24d092826
- https://git.kernel.org/stable/c/b0028f333420a65a53a63978522db680b37379dd
- https://git.kernel.org/stable/c/d9c54763e5cdbbd3f81868597fe8aca3c96e6387
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26638.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26638
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
