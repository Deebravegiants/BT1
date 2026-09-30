# [H] greybus: raw: fix use-after-free on cdev close

## Summary
Severity: High
Advisory: CVE-2026-53025
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-53025
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <7.0.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

greybus: raw: fix use-after-free on cdev close

This addresses a use-after-free bug when a raw bundle is disconnected
but its chardev is still opened by an application. When the application
releases the cdev, it causes the following panic when init on free is
enabled (CONFIG_INIT_ON_FREE_DEFAULT_ON=y):

        refcount_t: underflow; use-after-free.
        WARNING: CPU: 0 PID: 139 at lib/refcount.c:28 refcount_warn_saturate+0xd0/0x130
         ...
        Call Trace:
         <TASK>
         cdev_put+0x18/0x30
         __fput+0x255/0x2a0
         __x64_sys_close+0x3d/0x80
         do_syscall_64+0xa4/0x290
         entry_SYSCALL_64_after_hwframe+0x77/0x7f

The cdev is contained in the "gb_raw" structure, which is freed in the
disconnect operation. When the cdev is released at a later time,
cdev_put gets an address that points to freed memory.

To fix this use-after-free, convert the struct device from a pointer to
being embedded, that makes the lifetime of the cdev and of this device
the same. Then, use cdev_device_add, which guarantees that the device
won't be released until all references to the cdev have been released.
Finally, delegate the freeing of the structure to the device release
function, instead of freeing immediately in the disconnect callback.

## References
- https://git.kernel.org/stable/c/983cc2c7efbce04ecbf6328448d895044dd6ab31
- https://git.kernel.org/stable/c/ef2d97c15b19b3489de01695bce478601e236c3e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53025.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53025
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
