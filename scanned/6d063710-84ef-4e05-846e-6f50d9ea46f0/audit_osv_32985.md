# [H] iio: accel: fxls8962af: Fix use after free in fxls8962af_fifo_flush

## Summary
Severity: High
Advisory: CVE-2025-38485
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-38485
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.147, >=6.2.0 <6.6.100, >=6.7.0 <6.12.40, >=6.13.0 <6.15.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: accel: fxls8962af: Fix use after free in fxls8962af_fifo_flush

fxls8962af_fifo_flush() uses indio_dev->active_scan_mask (with
iio_for_each_active_channel()) without making sure the indio_dev
stays in buffer mode.
There is a race if indio_dev exits buffer mode in the middle of the
interrupt that flushes the fifo. Fix this by calling
synchronize_irq() to ensure that no interrupt is currently running when
disabling buffer mode.

Unable to handle kernel NULL pointer dereference at virtual address 00000000 when read
[...]
_find_first_bit_le from fxls8962af_fifo_flush+0x17c/0x290
fxls8962af_fifo_flush from fxls8962af_interrupt+0x80/0x178
fxls8962af_interrupt from irq_thread_fn+0x1c/0x7c
irq_thread_fn from irq_thread+0x110/0x1f4
irq_thread from kthread+0xe0/0xfc
kthread from ret_from_fork+0x14/0x2c

## References
- https://git.kernel.org/stable/c/1803d372460aaa9ae0188a30c9421d3f157f2f04
- https://git.kernel.org/stable/c/1fe16dc1a2f5057772e5391ec042ed7442966c9a
- https://git.kernel.org/stable/c/6ecd61c201b27ad2760b3975437ad2b97d725b98
- https://git.kernel.org/stable/c/bfcda3e1015791b3a63fb4d3aad408da9cf76e8f
- https://git.kernel.org/stable/c/dda42f23a8f5439eaac9521ce0531547d880cc54
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38485.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38485
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
