# [M] CVE-2017-14860

## Summary
Severity: Medium
Advisory: CVE-2017-14860
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2017-14860
Type: osv

## Details
There is a heap-based buffer over-read in the Exiv2::Jp2Image::readMetadata function of jp2image.cpp in Exiv2 0.26. A Crafted input will lead to a denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1494776
