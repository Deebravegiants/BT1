# [H] dmaengine: idxd: fix fdev setup failure cleanup in idxd_cdev_open()

## Summary
Severity: High
Advisory: CVE-2026-74574
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74574
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

dmaengine: idxd: fix fdev setup failure cleanup in idxd_cdev_open()

The failed_dev_add and failed_dev_name paths drop the file-device
reference while wq->wq_lock is still held. If put_device(fdev) drops the
last reference, idxd_file_dev_release() runs synchronously and tries to
take wq->wq_lock again, deadlocking.

Those paths also fall through into the later ctx cleanup labels even
though idxd_file_dev_release() owns that cleanup and frees ctx. This can
make idxd_xa_pasid_remove(ctx) and kfree(ctx) operate on a freed context.

Move idxd_wq_get() before file-device setup can fail, since the release
callback always calls idxd_wq_put(). Then unlock wq->wq_lock before
put_device(fdev) and return directly from the file-device setup failure
path, leaving ctx cleanup to the release callback.

## References
- https://git.kernel.org/stable/c/0679c0c189d2548f00e1bac95be28e2df5c6c7f7
- https://git.kernel.org/stable/c/6e26a41c4c1a706edaaa7c7dffc6b3b945707a55
- https://git.kernel.org/stable/c/778ccbded2c8749c5be7f0dfa04fc9977a36fb7e
- https://git.kernel.org/stable/c/8d5d28285728be47c82fdf1c48be4268293c90e7
- https://git.kernel.org/stable/c/ee1d7274102285d78a53161fc705a8d8cd40b066
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74574.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74574
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
