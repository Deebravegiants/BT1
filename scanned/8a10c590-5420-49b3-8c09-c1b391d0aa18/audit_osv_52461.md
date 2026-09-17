# [H] CVE-2021-47474

## Summary
Severity: High
Advisory: CVE-2021-47474
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47474
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

comedi: vmk80xx: fix bulk-buffer overflow

The driver is using endpoint-sized buffers but must not assume that the
tx and rx buffers are of equal size or a malicious device could overflow
the slab-allocated receive buffer when doing bulk transfers.

## References
- https://git.kernel.org/stable/c/0866dcaa828c21bc2f94dac00e086078f11b5772
- https://git.kernel.org/stable/c/1ae4715121a57bc6fa29fd992127b01907f2f993
- https://git.kernel.org/stable/c/78cdfd62bd54af615fba9e3ca1ba35de39d3871d
- https://git.kernel.org/stable/c/7b0e356189327287d0eb98ec081bd6dd97068cd3
- https://git.kernel.org/stable/c/e0e6a63fd97ad95fe05dfd77268a1952551e11a7
- https://git.kernel.org/stable/c/063f576c43d589a4c153554b681d32b3f8317c7b
- https://git.kernel.org/stable/c/47b4636ebdbeba2044b3db937c4d2b6a4fe3d0f2
- https://git.kernel.org/stable/c/7cfb35db607760698d299fd1cf7402dfa8f09973
- https://git.kernel.org/stable/c/b7fd7f3387f070215e6be341e68eb5c087eeecc0
