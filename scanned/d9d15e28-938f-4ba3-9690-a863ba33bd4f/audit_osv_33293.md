# [H] net/9p: fix double req put in p9_fd_cancelled

## Summary
Severity: High
Advisory: CVE-2025-40027
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40027
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.4.301, >=5.5.0 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.111, >=6.7.0 <6.12.52, >=6.13.0 <6.16.12, >=6.17.0 <6.17.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/9p: fix double req put in p9_fd_cancelled

Syzkaller reports a KASAN issue as below:

general protection fault, probably for non-canonical address 0xfbd59c0000000021: 0000 [#1] PREEMPT SMP KASAN NOPTI
KASAN: maybe wild-memory-access in range [0xdead000000000108-0xdead00000000010f]
CPU: 0 PID: 5083 Comm: syz-executor.2 Not tainted 6.1.134-syzkaller-00037-g855bd1d7d838 #0
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.12.0-1 04/01/2014
RIP: 0010:__list_del include/linux/list.h:114 [inline]
RIP: 0010:__list_del_entry include/linux/list.h:137 [inline]
RIP: 0010:list_del include/linux/list.h:148 [inline]
RIP: 0010:p9_fd_cancelled+0xe9/0x200 net/9p/trans_fd.c:734

Call Trace:
 <TASK>
 p9_client_flush+0x351/0x440 net/9p/client.c:614
 p9_client_rpc+0xb6b/0xc70 net/9p/client.c:734
 p9_client_version net/9p/client.c:920 [inline]
 p9_client_create+0xb51/0x1240 net/9p/client.c:1027
 v9fs_session_init+0x1f0/0x18f0 fs/9p/v9fs.c:408
 v9fs_mount+0xba/0xcb0 fs/9p/vfs_super.c:126
 legacy_get_tree+0x108/0x220 fs/fs_context.c:632
 vfs_get_tree+0x8e/0x300 fs/super.c:1573
 do_new_mount fs/namespace.c:3056 [inline]
 path_mount+0x6a6/0x1e90 fs/namespace.c:3386
 do_mount fs/namespace.c:3399 [inline]
 __do_sys_mount fs/namespace.c:3607 [inline]
 __se_sys_mount fs/namespace.c:3584 [inline]
 __x64_sys_mount+0x283/0x300 fs/namespace.c:3584
 do_syscall_x64 arch/x86/entry/common.c:51 [inline]
 do_syscall_64+0x35/0x80 arch/x86/entry/common.c:81
 entry_SYSCALL_64_after_hwframe+0x6e/0xd8

This happens because of a race condition between:

- The 9p client sending an invalid flush request and later cleaning it up;
- The 9p client in p9_read_work() canceled all pending requests.

      Thread 1                              Thread 2
    ...
    p9_client_create()
    ...
    p9_fd_create()
    ...
    p9_conn_create()
    ...
    // start Thread 2
    INIT_WORK(&m->rq, p9_read_work);
                                        p9_read_work()
    ...
    p9_client_rpc()
    ...
                                        ...
                                        p9_conn_cancel()
                                        ...
                                        spin_lock(&m->req_lock);
    ...
    p9_fd_cancelled()
    ...
                                        ...
                                        spin_unlock(&m->req_lock);
                                        // status rewrite
                                        p9_client_cb(m->client, req, REQ_STATUS_ERROR)
                                        // first remove
                                        list_del(&req->req_list);
                                        ...

    spin_lock(&m->req_lock)
    ...
    // second remove
    list_del(&req->req_list);
    spin_unlock(&m->req_lock)
  ...

Commit 74d6a5d56629 ("9p/trans_fd: Fix concurrency del of req_list in
p9_fd_cancelled/p9_read_work") fixes a concurrency issue in the 9p filesystem
client where the req_list could be deleted simultaneously by both
p9_read_work and p9_fd_cancelled functions, but for the case where req->status
equals REQ_STATUS_RCVD.

Update the check for req->status in p9_fd_cancelled to skip processing not
just received requests, but anything that is not SENT, as whatever
changed the state from SENT also removed the request from its list.

Found by Linux Verification Center (linuxtesting.org) with Syzkaller.

[updated the check from status == RECV || status == ERROR to status != SENT]

## References
- https://git.kernel.org/stable/c/0e0097005abc02c9f262370674f855625f4f3fb4
- https://git.kernel.org/stable/c/284e67a93b8c48952b6fc82129a8d3eb9dc73b06
- https://git.kernel.org/stable/c/448db01a48e1cdbbc31c995716a5dac1e52ba036
- https://git.kernel.org/stable/c/5c64c0b7b3446f7ed088a13bc8d7487d66534cbb
- https://git.kernel.org/stable/c/674b56aa57f9379854cb6798c3bbcef7e7b51ab7
- https://git.kernel.org/stable/c/716dceb19a9f8ff6c9d3aee5a771a93d6a47a0b6
- https://git.kernel.org/stable/c/94797b84cb9985022eb9cb3275c9497fbc883bb6
- https://git.kernel.org/stable/c/a5901a0dfb5964525990106706ae8b98db098226
- https://git.kernel.org/stable/c/c1db864270eb7fea94a9ef201da0c9dc1cbab7b8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40027.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40027
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
