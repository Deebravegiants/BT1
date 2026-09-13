# [M] CVE-2017-17724

## Summary
Severity: Medium
Advisory: CVE-2017-17724
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-02-12
Source: https://osv.dev/vulnerability/CVE-2017-17724
Type: osv

## Details
In Exiv2 0.26, there is a heap-based buffer over-read in the Exiv2::IptcData::printStructure function in iptc.cpp, related to the "!= 0x1c" case. Remote attackers can exploit this vulnerability to cause a denial of service via a crafted TIFF file.

## References
- https://github.com/xiaoqx/pocs/blob/master/exiv2/readme.md
- https://access.redhat.com/errata/RHSA-2019:2101
- https://security.gentoo.org/glsa/201811-14
- https://bugzilla.redhat.com/show_bug.cgi?id=1524107
- https://github.com/Exiv2/exiv2/issues/263
