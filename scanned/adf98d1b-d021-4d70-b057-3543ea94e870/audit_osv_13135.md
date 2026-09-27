# [M] CVE-2018-17854

## Summary
Severity: Medium
Advisory: CVE-2018-17854
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-01
Source: https://osv.dev/vulnerability/CVE-2018-17854
Type: osv

## Details
SIMDComp before 0.1.1 allows remote attackers to cause a denial of service (heap-based buffer over-read and application crash) because it can read (and then discard) extra bytes. NOTE: this issue exists because of an incomplete fix for CVE-2018-17427.

## References
- https://github.com/lemire/simdcomp/issues/21
