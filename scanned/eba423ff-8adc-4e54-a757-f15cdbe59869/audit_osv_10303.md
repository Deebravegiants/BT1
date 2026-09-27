# [M] CVE-2017-14861

## Summary
Severity: Medium
Advisory: CVE-2017-14861
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-09-29
Source: https://osv.dev/vulnerability/CVE-2017-14861
Type: osv

## Details
There is a stack consumption vulnerability in the Exiv2::Internal::stringFormat function of image.cpp in Exiv2 0.26. A Crafted input will lead to a remote denial of service attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1494787
