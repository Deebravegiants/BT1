# [H] CVE-2021-47361

## Summary
Severity: High
Advisory: CVE-2021-47361
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47361
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

mcb: fix error handling in mcb_alloc_bus()

There are two bugs:
1) If ida_simple_get() fails then this code calls put_device(carrier)
   but we haven't yet called get_device(carrier) and probably that
   leads to a use after free.
2) After device_initialize() then we need to use put_device() to
   release the bus.  This will free the internal resources tied to the
   device and call mcb_free_bus() which will free the rest.

## References
- https://git.kernel.org/stable/c/9fc198f415dee070a1de957bb5bf5921d8df3499
- https://git.kernel.org/stable/c/115b07d9f47e3996430b8f2007edd9768e1f807f
- https://git.kernel.org/stable/c/25a1433216489de4abc889910f744e952cb6dbae
- https://git.kernel.org/stable/c/66f74ba9be9daf9c47fface6af3677f602774f6b
- https://git.kernel.org/stable/c/7751f609eadf36b1f53712bae430019c53a16eb0
- https://git.kernel.org/stable/c/8a558261fa57a6deefb0925ab1829f698b194aea
- https://git.kernel.org/stable/c/91e4ad05bf18322b5921d1a6c9b603f6eb1694f0
