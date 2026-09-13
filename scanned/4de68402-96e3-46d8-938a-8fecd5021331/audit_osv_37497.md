# [C] ksmbd: fix use-after-free in __ksmbd_close_fd() via durable scavenger

## Summary
Severity: Critical
Advisory: CVE-2026-31718
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31718
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.6.140, >=6.7.0 <6.12.84, >=6.9.0 <6.18.25, >=6.13.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix use-after-free in __ksmbd_close_fd() via durable scavenger

When a durable file handle survives session disconnect (TCP close without
SMB2_LOGOFF), session_fd_check() sets fp->conn = NULL to preserve the
handle for later reconnection. However, it did not clean up the byte-range
locks on fp->lock_list.

Later, when the durable scavenger thread times out and calls
__ksmbd_close_fd(NULL, fp), the lock cleanup loop did:

    spin_lock(&fp->conn->llist_lock);

This caused a slab use-after-free because fp->conn was NULL and the
original connection object had already been freed by
ksmbd_tcp_disconnect().

The root cause is asymmetric cleanup: lock entries (smb_lock->clist) were
left dangling on the freed conn->lock_list while fp->conn was nulled out.

To fix this issue properly, we need to handle the lifetime of
smb_lock->clist across three paths:
 - Safely skip clist deletion when list is empty and fp->conn is NULL.
 - Remove the lock from the old connection's lock_list in
   session_fd_check()
 - Re-add the lock to the new connection's lock_list in
   ksmbd_reopen_durable_fd().

## References
- https://git.kernel.org/stable/c/0000a7780e0e446a28a273572f6ea8f7f582f694
- https://git.kernel.org/stable/c/235e32320a470fcd3998fb3774f2290a0eb302a1
- https://git.kernel.org/stable/c/3d6682726c2d3a46d31dae88b8166786b09b03ad
- https://git.kernel.org/stable/c/b34fc42cfe922e551f7a27d3ac3bb016e41d7dd9
- https://git.kernel.org/stable/c/e33c65f011980b4ad4abfd93585ec2079856368f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31718.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31718
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
