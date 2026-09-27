# [H] CVE-2018-9144

## Summary
Severity: High
Advisory: CVE-2018-9144
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-03-30
Source: https://osv.dev/vulnerability/CVE-2018-9144
Type: osv

## Details
In Exiv2 0.26, there is an out-of-bounds read in Exiv2::Internal::binaryToString in image.cpp. It could result in denial of service or information disclosure.

## References
- https://security.gentoo.org/glsa/201811-14
- https://github.com/Exiv2/exiv2/issues/254
- https://github.com/xiaoqx/pocs/tree/master/exiv2
