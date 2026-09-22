# [H] CVE-2018-18193

## Summary
Severity: High
Advisory: CVE-2018-18193
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-10-09
Source: https://osv.dev/vulnerability/CVE-2018-18193
Type: osv

## Details
An issue was discovered in libgig 4.1.0. There is operator new[] failure (due to a big pWavePoolTable heap request) in DLS::File::File in DLS.cpp.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/libgig/README-1008.md
