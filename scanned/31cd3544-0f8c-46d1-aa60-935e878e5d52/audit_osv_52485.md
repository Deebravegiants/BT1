# [H] CVE-2021-47500

## Summary
Severity: High
Advisory: CVE-2021-47500
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47500
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: mma8452: Fix trigger reference couting

The mma8452 driver directly assigns a trigger to the struct iio_dev. The
IIO core when done using this trigger will call `iio_trigger_put()` to drop
the reference count by 1.

Without the matching `iio_trigger_get()` in the driver the reference count
can reach 0 too early, the trigger gets freed while still in use and a
use-after-free occurs.

Fix this by getting a reference to the trigger before assigning it to the
IIO device.

## References
- https://git.kernel.org/stable/c/794c0898f6bf39a458655d5fb4af70ec43a5cfcb
- https://git.kernel.org/stable/c/acf0088ac073ca6e7f4cad6acac112177e08df5e
- https://git.kernel.org/stable/c/c43517071dfc9fce34f8f69dbb98a86017f6b739
- https://git.kernel.org/stable/c/cd0082235783f814241a1c9483fb89e405f4f892
- https://git.kernel.org/stable/c/db12d95085367de8b0223929d1332731024441f1
- https://git.kernel.org/stable/c/f5deab10ced368c807866283f8b79144c4823be8
- https://git.kernel.org/stable/c/fb75cc4740d81264cd5bcb0e17d961d018a8be96
- https://git.kernel.org/stable/c/094d513b78b1714113bc016684b8142382e071ba
