# [H] ksmbd: fix use-after-free of a deferred file_lock on double SMB2_CANCEL

## Summary
Severity: High
Advisory: CVE-2026-53198
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53198
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free of a deferred file_lock on double SMB2_CANCEL

A deferred byte-range lock (an SMB2_LOCK that blocks) registers an async work on
conn->async_requests via setup_async_work(), with cancel_fn =
smb2_remove_blocked_lock and cancel_argv[0] pointing at the struct file_lock.

When the request is cancelled, the worker frees the file_lock with
locks_free_lock() and takes the cancelled early-exit, which "goto out"s and never
reaches release_async_work() -- the only site that unlinks the work from
conn->async_requests and clears cancel_fn/cancel_argv. The work therefore stays
matchable on async_requests with a live cancel_fn pointing at the freed file_lock,
until connection teardown finally runs release_async_work().

smb2_cancel() fires cancel_fn unconditionally with no state guard, so a second
SMB2_CANCEL for the same AsyncId, arriving in that window, re-runs
smb2_remove_blocked_lock() on the freed file_lock -- a slab use-after-free:

  BUG: KASAN: slab-use-after-free in __locks_delete_block
    __locks_delete_block
    locks_delete_block
    ksmbd_vfs_posix_lock_unblock
    smb2_remove_blocked_lock
    smb2_cancel                 <- 2nd SMB2_CANCEL fires cancel_fn
    handle_ksmbd_work
  Allocated by ...: locks_alloc_lock <- smb2_lock
  Freed by ...:     locks_free_lock  <- smb2_lock (cancelled branch)
  ... cache file_lock_cache of size 192

Reproduced on mainline with KASAN by an authenticated SMB client.

Skip a work whose state is already KSMBD_WORK_CANCELLED so its cancel callback
cannot be fired a second time.

## References
- https://git.kernel.org/stable/c/0da2e073f9cbf4985a0fd9acb71bc5ff599f8afd
- https://git.kernel.org/stable/c/14d2eee0193ac3cd1bf3d014373449f0b8d35d6d
- https://git.kernel.org/stable/c/2b2eda2821cff1d1b5a423b6ee7d8fc6fbc8e694
- https://git.kernel.org/stable/c/89ae9df09d2c1fb4a4eb495c113a7ce1dca34147
- https://git.kernel.org/stable/c/b7063c7426ea5a4d15e01b60538718765392f49d
- https://git.kernel.org/stable/c/f580d27e8928828693df44ba2db0fffdbe11dfea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53198.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53198
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
