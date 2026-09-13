# [C] ksmbd: fix use-after-free of fp->owner.name in durable handle owner check

## Summary
Severity: Critical
Advisory: CVE-2026-72381
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72381
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free of fp->owner.name in durable handle owner check

Two concurrent SMB2 durable reconnects (DH2C/DHnC) on the same
persistent_id race the fp->owner.name compare-read in
ksmbd_vfs_compare_durable_owner() against the kfree() in
ksmbd_reopen_durable_fd()'s reopen-success path. fp->owner.name is a
standalone kstrdup() buffer whose lifetime is independent of the fp
refcount, and the two sites share no lock: the compare reads the buffer
while the reopen frees it, so the strcmp() can dereference freed memory.

Commit 7ce4fc40018d ("ksmbd: fix durable reconnect double-bind race in
ksmbd_reopen_durable_fd") made the fp->conn claim atomic under
global_ft.lock (closing the owner.name double-free and the ksmbd_file
write-UAF), but the compare-read versus reopen-free pair was left
unserialized.

  BUG: KASAN: slab-use-after-free in strcmp+0x2c/0x80
  Read of size 1 by task kworker
    strcmp
    ksmbd_vfs_compare_durable_owner
    smb2_check_durable_oplock
    smb2_open
  Freed by task kworker:
    kfree
    ksmbd_reopen_durable_fd
    smb2_open
  Allocated by task kworker:
    kstrdup
    session_fd_check
    smb2_session_logoff
  The buggy address belongs to the cache kmalloc-8

Serialize both sides of the race with fp->f_lock.  The global durable
file-table lock still protects the durable reconnect claim, but
fp->owner.name is per-open state and does not need to block unrelated
durable table lookups or reconnects.  The teardown is left at its
existing location after the reopen-success point so that an __open_id()
rollback still retains owner.name for a later legitimate reconnect to
verify.

## References
- https://git.kernel.org/stable/c/38637163501fd9e2f684b8cd275d0db5d79f37c6
- https://git.kernel.org/stable/c/5a5ac2852cd326529d02f778bc1aa6184701f4d7
- https://git.kernel.org/stable/c/93d4d46bf9d442a12ea87278049ec416962c627f
- https://git.kernel.org/stable/c/ed98719be41389d416953b8ef9f07a07dfea6b2b
- https://git.kernel.org/stable/c/fb978d72052704c6b06c6b0f129fcd60b77169f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72381.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72381
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
