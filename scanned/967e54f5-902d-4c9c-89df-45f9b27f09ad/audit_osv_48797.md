# [H] CVE-2018-14452

## Summary
Severity: High
Advisory: CVE-2018-14452
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-07-20
Source: https://osv.dev/vulnerability/CVE-2018-14452
Type: osv

## Details
An issue was discovered in libgig 4.1.0. There is an out-of-bounds read in the "always assign the sample of the first dimension region of this region" feature of the function gig::Region::UpdateChunks in gig.cpp.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/libgig/README.md
