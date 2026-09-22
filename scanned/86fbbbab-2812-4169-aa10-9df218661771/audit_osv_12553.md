# [C] CVE-2018-12889

## Summary
Severity: Critical
Advisory: CVE-2018-12889
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-12889
Type: osv

## Details
An issue was discovered in CCN-lite 2.0.1. There is a heap-based buffer overflow in mkAddToRelayCacheRequest and in ccnl_populate_cache for an array lacking '\0' termination when reading a binary CCNx or NDN file. This can result in Heap Corruption. This was addressed by fixing the memory management in mkAddToRelayCacheRequest in ccn-lite-ctrl.c.

## References
- https://github.com/cn-uofbasel/ccn-lite/issues/279
