# [H] CVE-2021-47280

## Summary
Severity: High
Advisory: CVE-2021-47280
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47280
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm: Fix use-after-free read in drm_getunique()

There is a time-of-check-to-time-of-use error in drm_getunique() due
to retrieving file_priv->master prior to locking the device's master
mutex.

An example can be seen in the crash report of the use-after-free error
found by Syzbot:
https://syzkaller.appspot.com/bug?id=148d2f1dfac64af52ffd27b661981a540724f803

In the report, the master pointer was used after being freed. This is
because another process had acquired the device's master mutex in
drm_setmaster_ioctl(), then overwrote fpriv->master in
drm_new_set_master(). The old value of fpriv->master was subsequently
freed before the mutex was unlocked.

To fix this, we lock the device's master mutex before retrieving the
pointer from from fpriv->master. This patch passes the Syzbot
reproducer test.

## References
- https://git.kernel.org/stable/c/f773f8cccac13c7e7bbd9182e7996c727742488e
- https://git.kernel.org/stable/c/17dab9326ff263c62dab1dbac4492e2938a049e4
- https://git.kernel.org/stable/c/491d52e0078860b33b6c14f0a7ac74ca1b603bd6
- https://git.kernel.org/stable/c/7d233ba700ceb593905ea82b42dadb4ec8ef85e9
- https://git.kernel.org/stable/c/b246b4c70c1250e7814f409b243000f9c0bf79a3
- https://git.kernel.org/stable/c/b436acd1cf7fac0ba987abd22955d98025c80c2b
