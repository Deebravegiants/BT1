# [H] gpio: cdev: make sure the cdev fd is still active before emitting events

## Summary
Severity: High
Advisory: CVE-2025-40249
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-04
Source: https://osv.dev/vulnerability/CVE-2025-40249
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.13.0 <6.17.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

gpio: cdev: make sure the cdev fd is still active before emitting events

With the final call to fput() on a file descriptor, the release action
may be deferred and scheduled on a work queue. The reference count of
that descriptor is still zero and it must not be used. It's possible
that a GPIO change, we want to notify the user-space about, happens
AFTER the reference count on the file descriptor associated with the
character device went down to zero but BEFORE the .release() callback
was called from the workqueue and so BEFORE we unregistered from the
notifier.

Using the regular get_file() routine in this situation triggers the
following warning:

  struct file::f_count incremented from zero; use-after-free condition present!

So use the get_file_active() variant that will return NULL on file
descriptors that have been or are being released.

## References
- https://git.kernel.org/stable/c/d4cd0902c156b2ca60fdda8cd8b5bcb4b0e9ed64
- https://git.kernel.org/stable/c/dccc6daa8afa0f64c432e4c867f275747e3415e1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40249.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40249
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
