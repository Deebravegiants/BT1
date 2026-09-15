# [M] CVE-2018-18192

## Summary
Severity: Medium
Advisory: CVE-2018-18192
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-10-09
Source: https://osv.dev/vulnerability/CVE-2018-18192
Type: osv

## Details
An issue was discovered in libgig 4.1.0. There is a NULL pointer dereference in the function DLS::File::GetFirstSample() in DLS.cpp.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/libgig/README-1008.md
