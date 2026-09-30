# [H] epoll: be better about file lifetimes

## Summary
Severity: High
Advisory: CVE-2024-38580
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-19
Source: https://osv.dev/vulnerability/CVE-2024-38580
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

epoll: be better about file lifetimes

epoll can call out to vfs_poll() with a file pointer that may race with
the last 'fput()'. That would make f_count go down to zero, and while
the ep->mtx locking means that the resulting file pointer tear-down will
be blocked until the poll returns, it means that f_count is already
dead, and any use of it won't actually get a reference to the file any
more: it's dead regardless.

Make sure we have a valid ref on the file pointer before we call down to
vfs_poll() from the epoll routines.

## References
- https://git.kernel.org/stable/c/16e3182f6322575eb7c12e728ad3c7986a189d5d
- https://git.kernel.org/stable/c/4efaa5acf0a1d2b5947f98abb3acf8bfd966422b
- https://git.kernel.org/stable/c/4f65f4defe4e23659275ce5153541cd4f76ce2d2
- https://git.kernel.org/stable/c/559214eb4e5c3d05e69428af2fae2691ba1eb784
- https://git.kernel.org/stable/c/cbfd1088e24ec4c1199756a37cb8e4cd0a4b016e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/38xxx/CVE-2024-38580.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-38580
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
