# [H] drm/xe: prevent UAF around preempt fence

## Summary
Severity: High
Advisory: CVE-2024-46683
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-13
Source: https://osv.dev/vulnerability/CVE-2024-46683
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/xe: prevent UAF around preempt fence

The fence lock is part of the queue, therefore in the current design
anything locking the fence should then also hold a ref to the queue to
prevent the queue from being freed.

However, currently it looks like we signal the fence and then drop the
queue ref, but if something is waiting on the fence, the waiter is
kicked to wake up at some later point, where upon waking up it first
grabs the lock before checking the fence state. But if we have already
dropped the queue ref, then the lock might already be freed as part of
the queue, leading to uaf.

To prevent this, move the fence lock into the fence itself so we don't
run into lifetime issues. Alternative might be to have device level
lock, or only release the queue in the fence release callback, however
that might require pushing to another worker to avoid locking issues.

References: https://gitlab.freedesktop.org/drm/xe/kernel/-/issues/2454
References: https://gitlab.freedesktop.org/drm/xe/kernel/-/issues/2342
References: https://gitlab.freedesktop.org/drm/xe/kernel/-/issues/2020
(cherry picked from commit 7116c35aacedc38be6d15bd21b2fc936eed0008b)

## References
- https://git.kernel.org/stable/c/10081b0b0ed201f53e24bd92deb2e0f3c3e713d4
- https://git.kernel.org/stable/c/730b72480e29f63fd644f5fa57c9d46109428953
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46683.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46683
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
