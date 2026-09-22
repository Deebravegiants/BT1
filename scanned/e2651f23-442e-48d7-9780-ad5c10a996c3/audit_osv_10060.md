# [M] CVE-2017-12957

## Summary
Severity: Medium
Advisory: CVE-2017-12957
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-08-18
Source: https://osv.dev/vulnerability/CVE-2017-12957
Type: osv

## Details
There is a heap-based buffer over-read in libexiv2 in Exiv2 0.26 that is triggered in the Exiv2::Image::io function in image.cpp. It will lead to remote denial of service.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1482423
