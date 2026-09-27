# [M] CVE-2021-47528

## Summary
Severity: Medium
Advisory: CVE-2021-47528
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47528
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: cdnsp: Fix a NULL pointer dereference in cdnsp_endpoint_init()

In cdnsp_endpoint_init(), cdnsp_ring_alloc() is assigned to pep->ring
and there is a dereference of it in cdnsp_endpoint_init(), which could
lead to a NULL pointer dereference on failure of cdnsp_ring_alloc().

Fix this bug by adding a check of pep->ring.

This bug was found by a static analyzer. The analysis employs
differential checking to identify inconsistent security operations
(e.g., checks or kfrees) between two code paths and confirms that the
inconsistent operations are not recovered in the current function or
the callers, so they constitute bugs.

Note that, as a bug found by static analysis, it can be a false
positive or hard to trigger. Multiple researchers have cross-reviewed
the bug.

Builds with CONFIG_USB_CDNSP_GADGET=y show no new warnings,
and our static analyzer no longer warns about this code.

## References
- https://git.kernel.org/stable/c/37307f7020ab38dde0892a578249bf63d00bca64
- https://git.kernel.org/stable/c/7d94bc8e335cb33918e52efdbe192c36707bfa24
