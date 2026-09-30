# [H] CVE-2017-17723

## Summary
Severity: High
Advisory: CVE-2017-17723
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2017-17723
Type: osv

## Details
In Exiv2 0.26, there is a heap-based buffer over-read in the Exiv2::Image::byteSwap4 function in image.cpp. Remote attackers can exploit this vulnerability to disclose memory data or cause a denial of service via a crafted TIFF file.

## References
- https://security.gentoo.org/glsa/201811-14
- https://bugzilla.redhat.com/show_bug.cgi?id=1524104
