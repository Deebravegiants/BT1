# [M] CVE-2019-20052

## Summary
Severity: Medium
Advisory: CVE-2019-20052
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2019-12-27
Source: https://osv.dev/vulnerability/CVE-2019-20052
Type: osv

## Details
A memory leak was discovered in Mat_VarCalloc in mat.c in matio 1.5.17 because SafeMulDims does not consider the rank==0 case.

## References
- https://github.com/tbeu/matio/issues/131
