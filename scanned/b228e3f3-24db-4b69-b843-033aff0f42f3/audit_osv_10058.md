# [H] CVE-2017-12955

## Summary
Severity: High
Advisory: CVE-2017-12955
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12955
Type: osv

## Details
There is a heap-based buffer overflow in basicio.cpp of Exiv2 0.26. The vulnerability causes an out-of-bounds write in Exiv2::Image::printIFDStructure(), which may lead to remote denial of service or possibly unspecified other impact.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1482295
