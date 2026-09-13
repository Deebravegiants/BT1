# [H] CVE-2018-14450

## Summary
Severity: High
Advisory: CVE-2018-14450
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2018-14450
Type: osv

## Details
An issue was discovered in libgig 4.1.0. There is an out-of-bounds read in the "update dimension region's chunks" feature of the function gig::Region::UpdateChunks in gig.cpp.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/libgig/README.md
