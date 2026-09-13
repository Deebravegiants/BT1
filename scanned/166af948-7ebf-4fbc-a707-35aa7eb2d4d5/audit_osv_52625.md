# [M] CVE-2021-47655

## Summary
Severity: Medium
Advisory: CVE-2021-47655
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47655
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: venus: vdec: fixed possible memory leak issue

The venus_helper_alloc_dpb_bufs() implementation allows an early return
on an error path when checking the id from ida_alloc_min() which would
not release the earlier buffer allocation.

Move the direct kfree() from the error checking of dma_alloc_attrs() to
the common fail path to ensure that allocations are released on all
error paths in this function.

Addresses-Coverity: 1494120 ("Resource leak")

## References
- https://git.kernel.org/stable/c/8403fdd775858a7bf04868d43daea0acbe49ddfc
- https://git.kernel.org/stable/c/55bccafc246b2e64763a155ec454470c07a54a6e
- https://git.kernel.org/stable/c/5cedfe8aaf1875a5305897107b7f298db4260019
- https://git.kernel.org/stable/c/5f89d05ba93df9c2cdfe493843f93288e55e99eb
