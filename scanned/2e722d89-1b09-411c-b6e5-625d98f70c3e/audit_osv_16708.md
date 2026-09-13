# [H] CVE-2019-9143

## Summary
Severity: High
Advisory: CVE-2019-9143
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-02-25
Source: https://osv.dev/vulnerability/CVE-2019-9143
Type: osv

## Details
An issue was discovered in Exiv2 0.27. There is infinite recursion at Exiv2::Image::printTiffStructure in the file image.cpp. This can be triggered by a crafted file. It allows an attacker to cause Denial of Service (Segmentation fault) or possibly have unspecified other impact.

## References
- http://www.securityfocus.com/bid/107161
- https://github.com/Exiv2/exiv2/issues/711
- https://research.loginsoft.com/bugs/uncontrolled-recursion-loop-in-exiv2imageprinttiffstructure-exiv2-0-27/
