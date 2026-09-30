# [M] CVE-2018-12232

## Summary
Severity: Medium
Advisory: CVE-2018-12232
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-06-12
Source: https://osv.dev/vulnerability/CVE-2018-12232
Type: osv

## Details
In net/socket.c in the Linux kernel through 4.17.1, there is a race condition between fchownat and close in cases where they target the same socket file descriptor, related to the sock_close and sockfs_setattr functions. fchownat does not increment the file descriptor reference count, which allows close to set the socket to NULL during fchownat's execution, leading to a NULL pointer dereference and system crash.

## References
- https://usn.ubuntu.com/3752-1/
- https://usn.ubuntu.com/3752-2/
- https://usn.ubuntu.com/3752-3/
- http://www.securityfocus.com/bid/104453
- https://access.redhat.com/errata/RHSA-2018:2948
- https://lkml.org/lkml/2018/6/5/14
- https://github.com/torvalds/linux/commit/6d8c50dcb029872b298eea68cc6209c866fd3e14
- https://patchwork.ozlabs.org/patch/926519/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6d8c50dcb029872b298eea68cc6209c866fd3e14
