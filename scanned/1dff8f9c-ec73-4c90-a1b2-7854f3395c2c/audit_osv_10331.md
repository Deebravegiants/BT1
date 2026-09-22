# [M] CVE-2017-14988

## Summary
Severity: Medium
Advisory: CVE-2017-14988
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-10-03
Source: https://osv.dev/vulnerability/CVE-2017-14988
Type: osv

## Details
Header::readfrom in IlmImf/ImfHeader.cpp in OpenEXR 2.2.0 allows remote attackers to cause a denial of service (excessive memory allocation) via a crafted file that is accessed with the ImfOpenInputFile function in IlmImf/ImfCRgbaFile.cpp. NOTE: The maintainer and multiple third parties believe that this vulnerability isn't valid

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00063.html
- https://github.com/openexr/openexr/issues/248
