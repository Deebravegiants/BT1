# [H] CVE-2016-1709

## Summary
Severity: High
Advisory: CVE-2016-1709
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-07-23
Source: https://osv.dev/vulnerability/CVE-2016-1709
Type: osv

## Details
Heap-based buffer overflow in the ByteArray::Get method in data/byte_array.cc in Google sfntly before 2016-06-10, as used in Google Chrome before 52.0.2743.82, allows remote attackers to cause a denial of service or possibly have unspecified other impact via a crafted SFNT font.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00020.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00022.html
- http://lists.opensuse.org/opensuse-security-announce/2016-07/msg00028.html
- http://www.securityfocus.com/bid/92053
- http://www.securitytracker.com/id/1036428
- https://crbug.com/614934
- http://rhn.redhat.com/errata/RHSA-2016-1485.html
- http://www.debian.org/security/2016/dsa-3637
- https://github.com/googlei18n/sfntly/commit/468cad540fa1b0027cad60456f53feabecdce2bc
- https://github.com/googlei18n/sfntly/commit/c56b85408bab232efd7e650f0994272a174e3b92
- https://github.com/googlei18n/sfntly/pull/56
- http://googlechromereleases.blogspot.com/2016/07/stable-channel-update.html
