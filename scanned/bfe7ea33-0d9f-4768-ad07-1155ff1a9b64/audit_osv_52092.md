# [H] CVE-2021-47061

## Summary
Severity: High
Advisory: CVE-2021-47061
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47061
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: Destroy I/O bus devices on unregister failure _after_ sync'ing SRCU

If allocating a new instance of an I/O bus fails when unregistering a
device, wait to destroy the device until after all readers are guaranteed
to see the new null bus.  Destroying devices before the bus is nullified
could lead to use-after-free since readers expect the devices on their
reference of the bus to remain valid.

## References
- https://git.kernel.org/stable/c/4e899ca848636b37e9ac124bc1723862a7d7d927
- https://git.kernel.org/stable/c/03c6cccedd3913006744faa252a4da5145299343
- https://git.kernel.org/stable/c/2ee3757424be7c1cd1d0bbfa6db29a7edd82a250
- https://git.kernel.org/stable/c/30f46c6993731efb2a690c9197c0fd9ed425da2d
