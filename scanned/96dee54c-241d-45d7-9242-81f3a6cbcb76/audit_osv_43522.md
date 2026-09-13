# [H] virtio: rtc: tear down old virtqueues before restore

## Summary
Severity: High
Advisory: CVE-2026-74311
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74311
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio: rtc: tear down old virtqueues before restore

virtio_device_restore() resets the device and restores the negotiated
features before calling ->restore(). viortc_freeze() intentionally
leaves the existing virtqueues in place so the alarm queue can still
wake the system, but viortc_restore() immediately calls
viortc_init_vqs() without first deleting those old queues.

If virtqueue reinitialization fails on virtio-pci, the transport error
path can run vp_del_vqs() against a newly allocated vp_dev->vqs array
while vdev->vqs still contains the old virtqueues. vp_del_vqs() then
looks up queue state through the new array and can dereference a NULL
info pointer in vp_del_vq(), crashing the guest kernel during restore.

This can also happen during a non-faulty reinitialization, when one of
the vp_find_vqs_msix() attempts is unsuccessful before a later attempt
would succeed.

Delete the stale virtqueues before rebuilding them. If restore fails
before virtio_device_ready(), reuse the remove path to stop the device.
Once the device is ready, return errors directly instead of deleting the
virtqueues again.

## References
- https://git.kernel.org/stable/c/548d2208455f14e6121404c6e30e997bfe0cd264
- https://git.kernel.org/stable/c/79366023aa891ca31376021a7bccff6384ca1ff1
- https://git.kernel.org/stable/c/aebebd1e9d70b650fc9e877082e0134edcf511da
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74311
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
