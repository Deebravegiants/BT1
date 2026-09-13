# [M] CVE-2018-20652

## Summary
Severity: Medium
Advisory: CVE-2018-20652
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-01-01
Source: https://osv.dev/vulnerability/CVE-2018-20652
Type: osv

## Details
An attempted excessive memory allocation was discovered in the function tinyexr::AllocateImage in tinyexr.h in tinyexr v0.9.5. Remote attackers could leverage this vulnerability to cause a denial-of-service via crafted input, which leads to an out-of-memory exception.

## References
- https://github.com/syoyo/tinyexr/issues/104
