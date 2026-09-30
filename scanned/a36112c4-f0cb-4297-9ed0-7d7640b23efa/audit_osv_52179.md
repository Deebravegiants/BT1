# [M] CVE-2021-47167

## Summary
Severity: Medium
Advisory: CVE-2021-47167
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47167
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

NFS: Fix an Oopsable condition in __nfs_pageio_add_request()

Ensure that nfs_pageio_error_cleanup() resets the mirror array contents,
so that the structure reflects the fact that it is now empty.
Also change the test in nfs_pageio_do_add_request() to be more robust by
checking whether or not the list is empty rather than relying on the
value of pg_count.

## References
- https://git.kernel.org/stable/c/1fc5f4eb9d31268ac3ce152d74ad5501ad24ca3e
- https://git.kernel.org/stable/c/56517ab958b7c11030e626250c00b9b1a24b41eb
- https://git.kernel.org/stable/c/ee21cd3aa8548e0cbc8c67a80b62113aedd2d101
- https://git.kernel.org/stable/c/15ac6f14787649e8ebd75c142e2c5d2a243c8490
