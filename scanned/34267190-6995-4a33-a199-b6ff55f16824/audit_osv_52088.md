# [M] CVE-2021-47057

## Summary
Severity: Medium
Advisory: CVE-2021-47057
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47057
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: sun8i-ss - Fix memory leak of object d when dma_iv fails to map

In the case where the dma_iv mapping fails, the return error path leaks
the memory allocated to object d.  Fix this by adding a new error return
label and jumping to this to ensure d is free'd before the return.

Addresses-Coverity: ("Resource leak")

## References
- https://git.kernel.org/stable/c/617ec35ed51f731a593ae7274228ef2cfc9cb781
- https://git.kernel.org/stable/c/6516cb852d704ff8d615de1f93cd443a99736c3d
- https://git.kernel.org/stable/c/98b5ef3e97b16eaeeedb936f8bda3594ff84a70e
- https://git.kernel.org/stable/c/e1f2d739849c3239df1ea3f97d40bade4b808410
