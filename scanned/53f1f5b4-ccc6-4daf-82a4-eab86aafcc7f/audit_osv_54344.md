# [M] CVE-2023-4969

## Summary
Severity: Medium
Advisory: CVE-2023-4969
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2024-01-16
Source: https://osv.dev/vulnerability/CVE-2023-4969
Type: osv

## Details
A GPU kernel can read sensitive data from another GPU kernel (even from another user or app) through an optimized GPU memory region called _local memory_ on various architectures.

## References
- https://kb.cert.org/vuls/id/446598
- https://registry.khronos.org/vulkan/specs/1.3-extensions/html/index.html
- https://www.kb.cert.org/vuls/id/446598
- https://registry.khronos.org/OpenCL/specs/3.0-unified/html/OpenCL_API.html#_fundamental_memory_regions
- https://blog.trailofbits.com
