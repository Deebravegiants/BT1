# [H] ax25: rcu protect dev->ax25_ptr

## Summary
Severity: High
Advisory: CVE-2025-21812
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2025-21812
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <6.1.129, >=6.2.0 <6.6.76, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: rcu protect dev->ax25_ptr

syzbot found a lockdep issue [1].

We should remove ax25 RTNL dependency in ax25_setsockopt()

This should also fix a variety of possible UAF in ax25.

[1]

WARNING: possible circular locking dependency detected
6.13.0-rc3-syzkaller-00762-g9268abe611b0 #0 Not tainted
------------------------------------------------------
syz.5.1818/12806 is trying to acquire lock:
 ffffffff8fcb3988 (rtnl_mutex){+.+.}-{4:4}, at: ax25_setsockopt+0xa55/0xe90 net/ax25/af_ax25.c:680

but task is already holding lock:
 ffff8880617ac258 (sk_lock-AF_AX25){+.+.}-{0:0}, at: lock_sock include/net/sock.h:1618 [inline]
 ffff8880617ac258 (sk_lock-AF_AX25){+.+.}-{0:0}, at: ax25_setsockopt+0x209/0xe90 net/ax25/af_ax25.c:574

which lock already depends on the new lock.

the existing dependency chain (in reverse order) is:

-> #1 (sk_lock-AF_AX25){+.+.}-{0:0}:
        lock_acquire+0x1ed/0x550 kernel/locking/lockdep.c:5849
        lock_sock_nested+0x48/0x100 net/core/sock.c:3642
        lock_sock include/net/sock.h:1618 [inline]
        ax25_kill_by_device net/ax25/af_ax25.c:101 [inline]
        ax25_device_event+0x24d/0x580 net/ax25/af_ax25.c:146
        notifier_call_chain+0x1a5/0x3f0 kernel/notifier.c:85
       __dev_notify_flags+0x207/0x400
        dev_change_flags+0xf0/0x1a0 net/core/dev.c:9026
        dev_ifsioc+0x7c8/0xe70 net/core/dev_ioctl.c:563
        dev_ioctl+0x719/0x1340 net/core/dev_ioctl.c:820
        sock_do_ioctl+0x240/0x460 net/socket.c:1234
        sock_ioctl+0x626/0x8e0 net/socket.c:1339
        vfs_ioctl fs/ioctl.c:51 [inline]
        __do_sys_ioctl fs/ioctl.c:906 [inline]
        __se_sys_ioctl+0xf5/0x170 fs/ioctl.c:892
        do_syscall_x64 arch/x86/entry/common.c:52 [inline]
        do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
       entry_SYSCALL_64_after_hwframe+0x77/0x7f

-> #0 (rtnl_mutex){+.+.}-{4:4}:
        check_prev_add kernel/locking/lockdep.c:3161 [inline]
        check_prevs_add kernel/locking/lockdep.c:3280 [inline]
        validate_chain+0x18ef/0x5920 kernel/locking/lockdep.c:3904
        __lock_acquire+0x1397/0x2100 kernel/locking/lockdep.c:5226
        lock_acquire+0x1ed/0x550 kernel/locking/lockdep.c:5849
        __mutex_lock_common kernel/locking/mutex.c:585 [inline]
        __mutex_lock+0x1ac/0xee0 kernel/locking/mutex.c:735
        ax25_setsockopt+0xa55/0xe90 net/ax25/af_ax25.c:680
        do_sock_setsockopt+0x3af/0x720 net/socket.c:2324
        __sys_setsockopt net/socket.c:2349 [inline]
        __do_sys_setsockopt net/socket.c:2355 [inline]
        __se_sys_setsockopt net/socket.c:2352 [inline]
        __x64_sys_setsockopt+0x1ee/0x280 net/socket.c:2352
        do_syscall_x64 arch/x86/entry/common.c:52 [inline]
        do_syscall_64+0xf3/0x230 arch/x86/entry/common.c:83
       entry_SYSCALL_64_after_hwframe+0x77/0x7f

other info that might help us debug this:

 Possible unsafe locking scenario:

       CPU0                    CPU1
       ----                    ----
  lock(sk_lock-AF_AX25);
                               lock(rtnl_mutex);
                               lock(sk_lock-AF_AX25);
  lock(rtnl_mutex);

 *** DEADLOCK ***

1 lock held by syz.5.1818/12806:
  #0: ffff8880617ac258 (sk_lock-AF_AX25){+.+.}-{0:0}, at: lock_sock include/net/sock.h:1618 [inline]
  #0: ffff8880617ac258 (sk_lock-AF_AX25){+.+.}-{0:0}, at: ax25_setsockopt+0x209/0xe90 net/ax25/af_ax25.c:574

stack backtrace:
CPU: 1 UID: 0 PID: 12806 Comm: syz.5.1818 Not tainted 6.13.0-rc3-syzkaller-00762-g9268abe611b0 #0
Hardware name: Google Google Compute Engine/Google Compute Engine, BIOS Google 09/13/2024
Call Trace:
 <TASK>
  __dump_stack lib/dump_stack.c:94 [inline]
  dump_stack_lvl+0x241/0x360 lib/dump_stack.c:120
  print_circular_bug+0x13a/0x1b0 kernel/locking/lockdep.c:2074
  check_noncircular+0x36a/0x4a0 kernel/locking/lockdep.c:2206
  check_prev_add kernel/locking/lockdep.c:3161 [inline]
  check_prevs_add kernel/lockin
---truncated---

## References
- https://git.kernel.org/stable/c/2802ed4ced27ebd474828fc67ffd7d66f11e3605
- https://git.kernel.org/stable/c/7705d8a7f2c26c80973c81093db07c6022b2b30e
- https://git.kernel.org/stable/c/8937f5e38a218531dce2a89fae60e3adcc2311e1
- https://git.kernel.org/stable/c/95fc45d1dea8e1253f8ec58abc5befb71553d666
- https://git.kernel.org/stable/c/c2531db6de3c95551be58878f859c6a053b7eb2e
- https://lists.debian.org/debian-lts-announce/2025/03/msg00028.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21812.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21812
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
