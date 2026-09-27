# [M] CVE-2021-47170

## Summary
Severity: Medium
Advisory: CVE-2021-47170
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47170
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

USB: usbfs: Don't WARN about excessively large memory allocations

Syzbot found that the kernel generates a WARNing if the user tries to
submit a bulk transfer through usbfs with a buffer that is way too
large.  This isn't a bug in the kernel; it's merely an invalid request
from the user and the usbfs code does handle it correctly.

In theory the same thing can happen with async transfers, or with the
packet descriptor table for isochronous transfers.

To prevent the MM subsystem from complaining about these bad
allocation requests, add the __GFP_NOWARN flag to the kmalloc calls
for these buffers.

## References
- https://git.kernel.org/stable/c/4f2629ea67e7225c3fd292c7fe4f5b3c9d6392de
- https://git.kernel.org/stable/c/8d83f109e920d2776991fa142bb904d985dca2ed
- https://git.kernel.org/stable/c/9f7cb3f01a10d9064cf13b3d26fb7e7a5827d098
- https://git.kernel.org/stable/c/2ab21d6e1411999b5fb43434f421f00bf50002eb
- https://git.kernel.org/stable/c/2c835fede13e03f2743a333e4370b5ed2db91e83
