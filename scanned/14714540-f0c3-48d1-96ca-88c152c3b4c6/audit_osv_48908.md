# [C] CVE-2018-18197

## Summary
Severity: Critical
Advisory: CVE-2018-18197
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-09
Source: https://osv.dev/vulnerability/CVE-2018-18197
Type: osv

## Details
An issue was discovered in libgig 4.1.0. There is an operator new[] failure (due to a big pSampleLoops heap request) in DLS::Sampler::Sampler in DLS.cpp.

## References
- https://github.com/TeamSeri0us/pocs/blob/master/libgig/README-1008.md
