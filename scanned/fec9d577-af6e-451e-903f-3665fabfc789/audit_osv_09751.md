# [M] CVE-2017-11338

## Summary
Severity: Medium
Advisory: CVE-2017-11338
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-07-17
Source: https://osv.dev/vulnerability/CVE-2017-11338
Type: osv

## Details
There is an infinite loop in the Exiv2::Image::printIFDStructure function of image.cpp in Exiv2 0.26. A crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1470913
