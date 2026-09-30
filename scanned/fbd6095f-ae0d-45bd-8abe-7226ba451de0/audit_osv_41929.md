# [H] rbd: eliminate a race in lock_dwork draining on unmap

## Summary
Severity: High
Advisory: CVE-2026-64112
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64112
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

rbd: eliminate a race in lock_dwork draining on unmap

Given how rbd_lock_add_request() and rbd_img_exclusive_lock() are
written, lock_dwork may be (re)queued more than it's actually needed:
for example in case a new I/O request comes in while we are in the
middle of rbd_acquire_lock() on behalf of another I/O request.  This is
expected and with rbd_release_lock() preemptively canceling lock_dwork
is benign under normal operation.

A more problematic example is maybe_kick_acquire():

    if (have_requests || delayed_work_pending(&rbd_dev->lock_dwork)) {
            dout("%s rbd_dev %p kicking lock_dwork\n", __func__, rbd_dev);
            mod_delayed_work(rbd_dev->task_wq, &rbd_dev->lock_dwork, 0);
    }

It's not unrealistic for lock_dwork to get canceled right after
delayed_work_pending() returns true and for mod_delayed_work() to
requeue it right there anyway.  This is a classic TOCTOU race.

When it comes to unmapping the image, there is an implicit assumption
of no self-initiated exclusive lock activity past the point of return
from rbd_dev_image_unlock() which unlocks the lock if it happens to be
held.  This unlock is assumed to be final and lock_dwork (as well as
all other exclusive lock tasks, really) isn't expected to get queued
again.  However, lock_dwork is canceled only in cancel_tasks_sync()
(i.e. later in the unmap sequence) and on top of that the cancellation
can get in effect nullified by maybe_kick_acquire().  This may result
in rbd_acquire_lock() executing after rbd_dev_device_release() and
rbd_dev_image_release() run and free and/or reset a bunch of things.
One of the possible failure modes then is a violated

    rbd_assert(rbd_image_format_valid(rbd_dev->image_format));

in rbd_dev_header_info() which is called via rbd_dev_refresh() from
rbd_post_acquire_action().

Redo exclusive lock task draining to provide saner semantics and try
to meet the assumptions around rbd_dev_image_unlock().

## References
- https://git.kernel.org/stable/c/3427d7ae38337066ce88b68302e285d344ab756b
- https://git.kernel.org/stable/c/9400efc76b42c751211974a25c91d2c19c65b01b
- https://git.kernel.org/stable/c/9dcd4f5c99b491c37be90b0bd9988db48225fb75
- https://git.kernel.org/stable/c/9fc75b71fdd38465c76c6f6a884cdd4ae3c72d90
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64112.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64112
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
