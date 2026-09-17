# [H] iio: buffer: Fix file related error handling in IIO_BUFFER_GET_FD_IOCTL

## Summary
Severity: High
Advisory: CVE-2022-48801
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-16
Source: https://osv.dev/vulnerability/CVE-2022-48801
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.24, >=5.16.0 <5.16.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

iio: buffer: Fix file related error handling in IIO_BUFFER_GET_FD_IOCTL

If we fail to copy the just created file descriptor to userland, we
try to clean up by putting back 'fd' and freeing 'ib'. The code uses
put_unused_fd() for the former which is wrong, as the file descriptor
was already published by fd_install() which gets called internally by
anon_inode_getfd().

This makes the error handling code leaving a half cleaned up file
descriptor table around and a partially destructed 'file' object,
allowing userland to play use-after-free tricks on us, by abusing
the still usable fd and making the code operate on a dangling
'file->private_data' pointer.

Instead of leaving the kernel in a partially corrupted state, don't
attempt to explicitly clean up and leave this to the process exit
path that'll release any still valid fds, including the one created
by the previous call to anon_inode_getfd(). Simply return -EFAULT to
indicate the error.

## References
- https://git.kernel.org/stable/c/202071d2518537866d291aa7cf26af54e674f4d4
- https://git.kernel.org/stable/c/b7f54894aa7517d2b6c797a499b9f491e9db9083
- https://git.kernel.org/stable/c/c72ea20503610a4a7ba26c769357d31602769c01
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48801.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48801
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
