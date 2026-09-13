# [M] CVE-2017-12956

## Summary
Severity: Medium
Advisory: CVE-2017-12956
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12956
Type: osv

## Details
There is an illegal address access in Exiv2::FileIo::path[abi:cxx11]() in basicio.cpp of libexiv2 in Exiv2 0.26 that will lead to remote denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1482296
