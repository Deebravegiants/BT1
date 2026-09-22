# [M] CVE-2017-18005

## Summary
Severity: Medium
Advisory: CVE-2017-18005
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-12-31
Source: https://osv.dev/vulnerability/CVE-2017-18005
Type: osv

## Details
Exiv2 0.26 has a Null Pointer Dereference in the Exiv2::DataValue::toLong function in value.cpp, related to crafted metadata in a TIFF file.

## References
- https://lists.debian.org/debian-lts-announce/2023/01/msg00004.html
- https://github.com/Exiv2/exiv2/issues/168
