# [M] bus: mhi: host: pci_generic: Use pci_try_reset_function() to avoid deadlock

## Summary
Severity: Medium
Advisory: CVE-2025-21951
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21951
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.12.0 <5.15.179, >=5.16.0 <6.1.131, >=6.2.0 <6.6.83, >=6.7.0 <6.12.19, >=6.13.0 <6.13.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: host: pci_generic: Use pci_try_reset_function() to avoid deadlock

There are multiple places from where the recovery work gets scheduled
asynchronously. Also, there are multiple places where the caller waits
synchronously for the recovery to be completed. One such place is during
the PM shutdown() callback.

If the device is not alive during recovery_work, it will try to reset the
device using pci_reset_function(). This function internally will take the
device_lock() first before resetting the device. By this time, if the lock
has already been acquired, then recovery_work will get stalled while
waiting for the lock. And if the lock was already acquired by the caller
which waits for the recovery_work to be completed, it will lead to
deadlock.

This is what happened on the X1E80100 CRD device when the device died
before shutdown() callback. Driver core calls the driver's shutdown()
callback while holding the device_lock() leading to deadlock.

And this deadlock scenario can occur on other paths as well, like during
the PM suspend() callback, where the driver core would hold the
device_lock() before calling driver's suspend() callback. And if the
recovery_work was already started, it could lead to deadlock. This is also
observed on the X1E80100 CRD.

So to fix both issues, use pci_try_reset_function() in recovery_work. This
function first checks for the availability of the device_lock() before
trying to reset the device. If the lock is available, it will acquire it
and reset the device. Otherwise, it will return -EAGAIN. If that happens,
recovery_work will fail with the error message "Recovery failed" as not
much could be done.

## References
- https://git.kernel.org/stable/c/1f9eb7078bc6b5fb5cbfbcb37c4bc01685332b95
- https://git.kernel.org/stable/c/62505657475c245c9cd46e42ac01026d1e61f027
- https://git.kernel.org/stable/c/7746f3bb8917fccb4571a576f3837d80fc513054
- https://git.kernel.org/stable/c/7a5ffadd54fe2662f5c99cdccf30144d060376f7
- https://git.kernel.org/stable/c/985d3cf56d8745ca637deee273929e01df449f85
- https://git.kernel.org/stable/c/a321d163de3d8aa38a6449ab2becf4b1581aed96
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21951.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21951
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
