# [M] CVE-2017-14863

## Summary
Severity: Medium
Advisory: CVE-2017-14863
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2017-14863
Type: osv

## Details
A NULL pointer dereference was discovered in Exiv2::Image::printIFDStructure in image.cpp in Exiv2 0.26. The vulnerability causes a segmentation fault and application crash, which leads to denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1494443
