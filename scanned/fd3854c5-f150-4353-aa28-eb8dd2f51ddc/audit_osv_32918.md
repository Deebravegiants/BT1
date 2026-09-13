# [H] virtio-pci: Fix result size returned for the admin command completion

## Summary
Severity: High
Advisory: CVE-2025-38314
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38314
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.15.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

virtio-pci: Fix result size returned for the admin command completion

The result size returned by virtio_pci_admin_dev_parts_get() is 8 bytes
larger than the actual result data size. This occurs because the
result_sg_size field of the command is filled with the result length
from virtqueue_get_buf(), which includes both the data size and an
additional 8 bytes of status.

This oversized result size causes two issues:
1. The state transferred to the destination includes 8 bytes of extra
   data at the end.
2. The allocated buffer in the kernel may be smaller than the returned
   size, leading to failures when reading beyond the allocated size.

The commit fixes this by subtracting the status size from the result of
virtqueue_get_buf().

This fix has been tested through live migrations with virtio-net,
virtio-net-transitional, and virtio-blk devices.

## References
- https://git.kernel.org/stable/c/920b6720bb63893b81516c0c45884a8350f9e4bf
- https://git.kernel.org/stable/c/9ef41ebf787fcbde99ac404ae473f8467641f983
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38314.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38314
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
