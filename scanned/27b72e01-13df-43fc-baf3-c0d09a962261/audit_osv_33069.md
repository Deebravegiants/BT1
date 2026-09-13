# [H] comedi: fix race between polling and detaching

## Summary
Severity: High
Advisory: CVE-2025-38687
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38687
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.14.0 <5.4.297, >=5.5.0 <5.10.241, >=5.11.0 <5.15.190, >=5.16.0 <6.1.149, >=6.2.0 <6.6.103, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: fix race between polling and detaching

syzbot reports a use-after-free in comedi in the below link, which is
due to comedi gladly removing the allocated async area even though poll
requests are still active on the wait_queue_head inside of it. This can
cause a use-after-free when the poll entries are later triggered or
removed, as the memory for the wait_queue_head has been freed.  We need
to check there are no tasks queued on any of the subdevices' wait queues
before allowing the device to be detached by the `COMEDI_DEVCONFIG`
ioctl.

Tasks will read-lock `dev->attach_lock` before adding themselves to the
subdevice wait queue, so fix the problem in the `COMEDI_DEVCONFIG` ioctl
handler by write-locking `dev->attach_lock` before checking that all of
the subdevices are safe to be deleted.  This includes testing for any
sleepers on the subdevices' wait queues.  It remains locked until the
device has been detached.  This requires the `comedi_device_detach()`
function to be refactored slightly, moving the bulk of it into new
function `comedi_device_detach_locked()`.

Note that the refactor of `comedi_device_detach()` results in
`comedi_device_cancel_all()` now being called while `dev->attach_lock`
is write-locked, which wasn't the case previously, but that does not
matter.

Thanks to Jens Axboe for diagnosing the problem and co-developing this
patch.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-032379.html
- https://git.kernel.org/stable/c/017198079551a2a5cf61eae966af3c4b145e1f3b
- https://git.kernel.org/stable/c/0f989f9d05492028afd2bded4b42023c57d8a76e
- https://git.kernel.org/stable/c/35b6fc51c666fc96355be5cd633ed0fe4ccf68b2
- https://git.kernel.org/stable/c/5724e82df4f9a4be62908362c97d522d25de75dd
- https://git.kernel.org/stable/c/5c4a2ffcbd052c69bbf4680677d4c4eaa5a252d4
- https://git.kernel.org/stable/c/71ca60d2e631cf9c63bcbc7017961c61ff04e419
- https://git.kernel.org/stable/c/cd4286123d6948ff638ea9cd5818ae4796d5d252
- https://git.kernel.org/stable/c/d85fac8729c9acfd72368faff1d576ec585e5c8f
- https://git.kernel.org/stable/c/fe67122ba781df44a1a9716eb1dfd751321ab512
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38687.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38687
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
