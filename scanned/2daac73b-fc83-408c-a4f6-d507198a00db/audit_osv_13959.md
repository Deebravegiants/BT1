# [M] CVE-2018-5772

## Summary
Severity: Medium
Advisory: CVE-2018-5772
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-01-18
Source: https://osv.dev/vulnerability/CVE-2018-5772
Type: osv

## Details
In Exiv2 0.26, there is a segmentation fault caused by uncontrolled recursion in the Exiv2::Image::printIFDStructure function in the image.cpp file. Remote attackers could leverage this vulnerability to cause a denial of service via a crafted tif file.

## References
- http://www.securityfocus.com/bid/102789
- https://security.gentoo.org/glsa/201811-14
- https://github.com/Exiv2/exiv2/issues/216
