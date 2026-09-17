# [H] iio: event: Fix event FIFO reset race

## Summary
Severity: High
Advisory: CVE-2026-64496
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64496
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.15.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: event: Fix event FIFO reset race

`iio_event_getfd()` creates the event file descriptor with
`anon_inode_getfd()`, which allocates a new fd, creates the anonymous
file and installs it in the process fd table before returning to the
caller.

The IIO code resets the event FIFO after `anon_inode_getfd()` has returned,
but before `IIO_GET_EVENT_FD_IOCTL` has copied the fd number to userspace.
But since fd tables are shared between threads, another thread can guess
the newly allocated fd number and issue a `read()` on it as soon as the fd
has been installed.

This means the `kfifo_to_user()` in `iio_event_chrdev_read()` can run in
parallel with the `kfifo_reset_out()` in `iio_event_getfd()`.

The kfifo documentation says that `kfifo_reset_out()` is only safe when it
is called from the reader thread and there is only one concurrent reader.
Otherwise it is dangerous and must be handled in the same way as
`kfifo_reset()`.

If that happens, `kfifo_to_user()` can advance the FIFO `out` index based
on state from before the reset, after the reset has already moved the `out`
index to the current `in` index. That can leave the FIFO with an `out`
index past the `in` index. A later `read()` can then see an underflowed
FIFO length and copy more data than the event FIFO buffer contains. This
can result in an out-of-bounds read and leak adjacent kernel memory to
userspace.

Move the FIFO reset before `anon_inode_getfd()`. At that point the event fd is
marked busy, but the new fd has not been installed yet, so userspace cannot
access it while the FIFO is reset.

## References
- https://git.kernel.org/stable/c/0d4a646d7f87ea3625fafe387043fddc6a2f5e7f
- https://git.kernel.org/stable/c/72c6aa8e0d74eab91b8694cde97dec088c248fee
- https://git.kernel.org/stable/c/9dc84ba4be5bbeb29ee49efe6cea2cb32c461424
- https://git.kernel.org/stable/c/9edefd4c56bee3fe331e0355d1f10a533134999d
- https://git.kernel.org/stable/c/a13ef1adbc62085b21b546b07b0be7e2fbf52150
- https://git.kernel.org/stable/c/af791d295737ea6b6ff2c8d8488462a49c14af01
- https://git.kernel.org/stable/c/d16a702ca7d29c0b7a9b509339d1b044a1cadb32
- https://git.kernel.org/stable/c/f187dc5a4c4846ffa07d9bda6e760837ed005574
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64496.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64496
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
