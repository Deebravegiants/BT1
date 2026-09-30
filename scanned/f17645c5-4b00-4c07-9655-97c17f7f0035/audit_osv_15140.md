# [M] CVE-2019-13959

## Summary
Severity: Medium
Advisory: CVE-2019-13959
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-07-18
Source: https://osv.dev/vulnerability/CVE-2019-13959
Type: osv

## Details
In Bento4 1.5.1-627, AP4_DataBuffer::SetDataSize does not handle reallocation failures, leading to a memory copy into a NULL pointer. This is different from CVE-2018-20186.

## References
- https://github.com/axiomatic-systems/Bento4/issues/394
