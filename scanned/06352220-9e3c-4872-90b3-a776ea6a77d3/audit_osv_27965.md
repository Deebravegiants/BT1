# [M] Bluetooth: af_bluetooth: Fix deadlock

## Summary
Severity: Medium
Advisory: CVE-2024-26886
Ecosystem: Linux
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-17
Source: https://osv.dev/vulnerability/CVE-2024-26886
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.15.209, >=5.16.0 <6.6.23, >=6.7.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: af_bluetooth: Fix deadlock

Attemting to do sock_lock on .recvmsg may cause a deadlock as shown
bellow, so instead of using sock_sock this uses sk_receive_queue.lock
on bt_sock_ioctl to avoid the UAF:

INFO: task kworker/u9:1:121 blocked for more than 30 seconds.
      Not tainted 6.7.6-lemon #183
Workqueue: hci0 hci_rx_work
Call Trace:
 <TASK>
 __schedule+0x37d/0xa00
 schedule+0x32/0xe0
 __lock_sock+0x68/0xa0
 ? __pfx_autoremove_wake_function+0x10/0x10
 lock_sock_nested+0x43/0x50
 l2cap_sock_recv_cb+0x21/0xa0
 l2cap_recv_frame+0x55b/0x30a0
 ? psi_task_switch+0xeb/0x270
 ? finish_task_switch.isra.0+0x93/0x2a0
 hci_rx_work+0x33a/0x3f0
 process_one_work+0x13a/0x2f0
 worker_thread+0x2f0/0x410
 ? __pfx_worker_thread+0x10/0x10
 kthread+0xe0/0x110
 ? __pfx_kthread+0x10/0x10
 ret_from_fork+0x2c/0x50
 ? __pfx_kthread+0x10/0x10
 ret_from_fork_asm+0x1b/0x30
 </TASK>

## References
- https://git.kernel.org/stable/c/2c9e2df022ef8b9d7fac58a04a2ef4ed25288955
- https://git.kernel.org/stable/c/60673f442984fe689d4127a5dd4be414247b3d67
- https://git.kernel.org/stable/c/64be3c6154886200708da0dfe259705fb992416c
- https://git.kernel.org/stable/c/817e8138ce86001b2fa5c63d6ede756e205a01f7
- https://git.kernel.org/stable/c/cb8adca52f306563d958a863bb0cbae9c184d1ae
- https://git.kernel.org/stable/c/f7b94bdc1ec107c92262716b073b3e816d4784fb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26886.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26886
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
