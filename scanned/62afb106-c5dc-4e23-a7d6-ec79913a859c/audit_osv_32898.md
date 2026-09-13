# [H] smb: client: fix potential deadlock when reconnecting channels

## Summary
Severity: High
Advisory: CVE-2025-38244
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38244
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix potential deadlock when reconnecting channels

Fix cifs_signal_cifsd_for_reconnect() to take the correct lock order
and prevent the following deadlock from happening

======================================================
WARNING: possible circular locking dependency detected
6.16.0-rc3-build2+ #1301 Tainted: G S      W
------------------------------------------------------
cifsd/6055 is trying to acquire lock:
ffff88810ad56038 (&tcp_ses->srv_lock){+.+.}-{3:3}, at: cifs_signal_cifsd_for_reconnect+0x134/0x200

but task is already holding lock:
ffff888119c64330 (&ret_buf->chan_lock){+.+.}-{3:3}, at: cifs_signal_cifsd_for_reconnect+0xcf/0x200

which lock already depends on the new lock.

the existing dependency chain (in reverse order) is:

-> #2 (&ret_buf->chan_lock){+.+.}-{3:3}:
       validate_chain+0x1cf/0x270
       __lock_acquire+0x60e/0x780
       lock_acquire.part.0+0xb4/0x1f0
       _raw_spin_lock+0x2f/0x40
       cifs_setup_session+0x81/0x4b0
       cifs_get_smb_ses+0x771/0x900
       cifs_mount_get_session+0x7e/0x170
       cifs_mount+0x92/0x2d0
       cifs_smb3_do_mount+0x161/0x460
       smb3_get_tree+0x55/0x90
       vfs_get_tree+0x46/0x180
       do_new_mount+0x1b0/0x2e0
       path_mount+0x6ee/0x740
       do_mount+0x98/0xe0
       __do_sys_mount+0x148/0x180
       do_syscall_64+0xa4/0x260
       entry_SYSCALL_64_after_hwframe+0x76/0x7e

-> #1 (&ret_buf->ses_lock){+.+.}-{3:3}:
       validate_chain+0x1cf/0x270
       __lock_acquire+0x60e/0x780
       lock_acquire.part.0+0xb4/0x1f0
       _raw_spin_lock+0x2f/0x40
       cifs_match_super+0x101/0x320
       sget+0xab/0x270
       cifs_smb3_do_mount+0x1e0/0x460
       smb3_get_tree+0x55/0x90
       vfs_get_tree+0x46/0x180
       do_new_mount+0x1b0/0x2e0
       path_mount+0x6ee/0x740
       do_mount+0x98/0xe0
       __do_sys_mount+0x148/0x180
       do_syscall_64+0xa4/0x260
       entry_SYSCALL_64_after_hwframe+0x76/0x7e

-> #0 (&tcp_ses->srv_lock){+.+.}-{3:3}:
       check_noncircular+0x95/0xc0
       check_prev_add+0x115/0x2f0
       validate_chain+0x1cf/0x270
       __lock_acquire+0x60e/0x780
       lock_acquire.part.0+0xb4/0x1f0
       _raw_spin_lock+0x2f/0x40
       cifs_signal_cifsd_for_reconnect+0x134/0x200
       __cifs_reconnect+0x8f/0x500
       cifs_handle_standard+0x112/0x280
       cifs_demultiplex_thread+0x64d/0xbc0
       kthread+0x2f7/0x310
       ret_from_fork+0x2a/0x230
       ret_from_fork_asm+0x1a/0x30

other info that might help us debug this:

Chain exists of:
  &tcp_ses->srv_lock --> &ret_buf->ses_lock --> &ret_buf->chan_lock

 Possible unsafe locking scenario:

       CPU0                    CPU1
       ----                    ----
  lock(&ret_buf->chan_lock);
                               lock(&ret_buf->ses_lock);
                               lock(&ret_buf->chan_lock);
  lock(&tcp_ses->srv_lock);

 *** DEADLOCK ***

3 locks held by cifsd/6055:
 #0: ffffffff857de398 (&cifs_tcp_ses_lock){+.+.}-{3:3}, at: cifs_signal_cifsd_for_reconnect+0x7b/0x200
 #1: ffff888119c64060 (&ret_buf->ses_lock){+.+.}-{3:3}, at: cifs_signal_cifsd_for_reconnect+0x9c/0x200
 #2: ffff888119c64330 (&ret_buf->chan_lock){+.+.}-{3:3}, at: cifs_signal_cifsd_for_reconnect+0xcf/0x200

## References
- https://git.kernel.org/stable/c/711741f94ac3cf9f4e3aa73aa171e76d188c0819
- https://git.kernel.org/stable/c/7f3ead8ebc0ef65b6c89a13912b4e80218425629
- https://git.kernel.org/stable/c/c82c7041258d96e3286f6790ab700e4edd3cc9e3
- https://git.kernel.org/stable/c/fe035dc78aa6ca8f862857d45beaf7a0e03206ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38244.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38244
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
