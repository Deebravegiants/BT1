# [M] CVE-2017-12924

## Summary
Severity: Medium
Advisory: CVE-2017-12924
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-28
Source: https://osv.dev/vulnerability/CVE-2017-12924
Type: osv

## Details
CDirVector::GetTable in dirfunc.hxx in libfpx 1.3.1_p6 allows remote attackers to cause a denial of service (divide-by-zero error) via a crafted fpx image.

## References
- http://www.openwall.com/lists/oss-security/2017/08/17/8
- https://blogs.gentoo.org/ago/2017/08/09/libfpx-divide-by-zero-in-cdirvectorgettable-dirfunc-hxx/
