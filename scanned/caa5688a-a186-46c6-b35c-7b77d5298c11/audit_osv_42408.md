# [H] audit: fix recursive locking deadlock in audit_dupe_exe()

## Summary
Severity: High
Advisory: CVE-2026-68096
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68096
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.3.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

audit: fix recursive locking deadlock in audit_dupe_exe()

A deadlock occurs in the audit subsystem when duplicating
executable-related rules.

When a file is moved (e.g., via do_renameat2()), the VFS layer locks
the parent directory (I_MUTEX_PARENT), which synchronously triggers an
fsnotify_move event. If an existing executable audit rule matches the
file being moved, the audit subsystem catches this event and calls
audit_dupe_exe() to duplicate the watch and update the rule. Then,
audit_alloc_mark() would call kern_path_parent() to resolve the path,
leading to a blind attempt to acquire the exact same I_MUTEX_PARENT lock
already held by the task, resulting in the following recursive locking
deadlock:

 ============================================
 WARNING: possible recursive locking detected
 6.12.0-55.27.1.el10_0.x86_64+debug #1 Not tainted
 --------------------------------------------
 mv/5099 is trying to acquire lock:
 ffff888132845358 (&inode->i_sb->s_type->i_mutex_dir_key/1){+.+.}-{3:3},
 at: __kern_path_locked+0x10a/0x2f0

 but task is already holding lock:
 ffff888132846b58 (&inode->i_sb->s_type->i_mutex_dir_key/1){+.+.}-{3:3},
 at: lock_two_directories+0x13f/0x2b0

 other info that might help us debug this:
  Possible unsafe locking scenario:

        CPU0
        ----
   lock(&inode->i_sb->s_type->i_mutex_dir_key/1);
   lock(&inode->i_sb->s_type->i_mutex_dir_key/1);

  *** DEADLOCK ***

  May be due to missing lock nesting notation

  6 locks held by mv/5099:
  #0: ffff888112a9c440 (sb_writers#13)
  at: do_renameat2+0x34c/0xbc0
  #1: ffff888112a9c790 (&type->s_vfs_rename_key#3)
  at: do_renameat2+0x415/0xbc0
  #2: ffff888132846b58 (&inode->i_sb->s_type->i_mutex_dir_key/1)
  at: lock_two_directories+0x13f/0x2b0
  #3: ffff888132845358 (&inode->i_sb->s_type->i_mutex_dir_key/5)
  at: lock_two_directories+0x175/0x2b0
  #4: ffffffffb3a1fb10 (&fsnotify_mark_srcu)
  at: fsnotify+0x454/0x28a0
  #5: ffffffffaf886230 (audit_filter_mutex)
  at: audit_update_watch+0x36/0x11e0

 stack backtrace:
 Call Trace:
  <TASK>
  dump_stack_lvl+0x6f/0xb0
  print_deadlock_bug.cold+0xbd/0xca
  validate_chain+0x83a/0xf00
  __lock_acquire+0xcac/0x1d20
  lock_acquire.part.0+0x11b/0x360
  down_write_nested+0x9f/0x230
  __kern_path_locked+0x10a/0x2f0
  kern_path_locked+0x26/0x40
  audit_alloc_mark+0xfb/0x4f0
  audit_dupe_exe+0x6c/0xe0
  audit_dupe_rule+0x6c2/0xc00
  audit_update_watch+0x4cc/0x11e0
  audit_watch_handle_event+0x12c/0x1b0
  send_to_group+0x5d0/0x8b0
  fsnotify+0x615/0x28a0
  fsnotify_move+0x1d8/0x630
  vfs_rename+0xdcd/0x1df0
  do_renameat2+0x9d4/0xbc0
  __x64_sys_renameat+0x192/0x260
  do_syscall_64+0x92/0x180
  entry_SYSCALL_64_after_hwframe+0x76/0x7e
 RIP: 0033:0x7f0491fe8c4e
 Code: 0f 1f 40 00 48 8b 15 c1 e1 16 00 f7 d8 64 89 02 b8 ff ff ff ff
 c3 66 0f 1f 44 00 00 f3 0f 1e fa 49 89 ca b8 08 01 00 00 0f 05 <48>
 3d 00 f0 ff ff 77 0a c3 66 0f 1f 84 00 00 00 00 00 48 8b 15 89
 RSP: 002b:00007ffc7210bf38 EFLAGS: 00000246 ORIG_RAX: 0000000000000108
 RAX: ffffffffffffffda RBX: 0000000000000000 RCX: 00007f0491fe8c4e
 RDX: 0000000000000003 RSI: 00007ffc7210e6c8 RDI: 00000000ffffff9c
 RBP: 0000000000000000 R08: 0000000000000000 R09: 0000000000000001
 R10: 00005575eb2dae2a R11: 0000000000000246 R12: 00005575eb2dae2a
 R13: 00007ffc7210e6c8 R14: 0000000000000003 R15: 00000000ffffff9c
  </TASK>

The aforementioned deadlock can be consistently reproduced by running
the script below:

 audit-dupe-exe-deadlock.sh
 --------------------------
 #!/bin/bash
 auditctl -D
 mkdir -p /tmp/foo
 touch /tmp/file
 auditctl -a always,exit -F exe=/tmp/file -F path=/tmp/file -S all -k dr
 mv /tmp/file /tmp/foo/file
 rm -Rf /tmp/foo

This patch fixes the issue by introducing struct audit_watch_ctx to pass
the fsnotify event context down to audit_alloc_mark(). By utilizing the
already-resolved directory inode provided by the event, we bypass the
kern_path_parent() path resol
---truncated---

## References
- https://git.kernel.org/stable/c/36eb77f14b4e6f2dc1008c1fabe31236397be27a
- https://git.kernel.org/stable/c/3b601938314c24fcd1afb6659cad92fe96c9c2f8
- https://git.kernel.org/stable/c/3bbb4931f7cd84cecf29ec222c0732bf9ad4da9f
- https://git.kernel.org/stable/c/40879c39d6740f3dddfb52b5d6ba7fb8cceb84d8
- https://git.kernel.org/stable/c/6114c3f21eb2ae175401736da744b684705e7ed9
- https://git.kernel.org/stable/c/7d1f66c69898ffb1a718926c32a777ecc471caca
- https://git.kernel.org/stable/c/81905b5acbe77284734438df3fbec1158e6429a3
- https://git.kernel.org/stable/c/f6fda0ac6661c23b8356dfb1cc423960cc6f0593
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68096.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68096
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
