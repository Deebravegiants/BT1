# [H] CVE-2018-9305

## Summary
Severity: High
Advisory: CVE-2018-9305
CVSS: 8.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9305
Type: osv

## Details
In Exiv2 0.26, an out-of-bounds read in IptcData::printStructure in iptc.c could result in a crash or information leak, related to the "== 0x1c" case.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-04/msg00009.html
- https://access.redhat.com/errata/RHSA-2019:2101
- https://security.gentoo.org/glsa/201811-14
- https://github.com/Exiv2/exiv2/issues/263
- https://github.com/xiaoqx/pocs/blob/master/exiv2/readme.md
