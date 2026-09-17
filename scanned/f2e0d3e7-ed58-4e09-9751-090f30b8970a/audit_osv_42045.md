# [H] ksmbd: fix UAF of struct file_lock in SMB2_LOCK deferred-lock cancellation

## Summary
Severity: High
Advisory: CVE-2026-64396
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64396
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

ksmbd: fix UAF of struct file_lock in SMB2_LOCK deferred-lock cancellation

When a blocking byte-range lock request is deferred in the
FILE_LOCK_DEFERRED path, ksmbd registers the asynchronous work into
the connection's async_requests list via setup_async_work(). The cancel
callback smb2_remove_blocked_lock() holds a reference to the flock.

If the lock waiter is subsequently woken up but the work state is no
longer KSMBD_WORK_ACTIVE (e.g., due to a concurrent cancellation), the
cleanup path calls locks_free_lock(flock) without dequeuing the work from
the async_requests list. Concurrently, smb2_cancel() walks the list
under conn->request_lock and invokes the cancel callback, which then
dereferences the already freed 'flock'. This leads to a slab-use-after-free
inside __wake_up_common.

Fix this by restructuring the cleanup logic after the worker returns
from ksmbd_vfs_posix_lock_wait(). Move list_del(&smb_lock->llist) and
release_async_work(work) to the top of the cleanup block. This guarantees
that the async work is completely dequeued and serialized under
conn->request_lock before locks_free_lock(flock) is called, rendering
the flock unreachable for any concurrent smb2_cancel().

## References
- https://git.kernel.org/stable/c/367c42a611fe488b7b03f1f6737f4dee0e8b20a2
- https://git.kernel.org/stable/c/463bbd79698513af4dad50fe1c573825f297ca2e
- https://git.kernel.org/stable/c/5aa1cb01155f96824003baf7997cdf1f150caba3
- https://git.kernel.org/stable/c/5c75275c0fc9a2deb0d8f5604edcb16f288171c8
- https://git.kernel.org/stable/c/7703fd9aba1f2483c8e55f9ff73b7663e0761ed9
- https://git.kernel.org/stable/c/d20d1c8ba5765d1d12eefc0aee6385ab3f240e1e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64396.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64396
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
