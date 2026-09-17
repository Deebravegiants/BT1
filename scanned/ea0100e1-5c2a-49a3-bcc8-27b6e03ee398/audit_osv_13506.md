# [M] CVE-2018-20098

## Summary
Severity: Medium
Advisory: CVE-2018-20098
Aliases: PYSEC-2018-119
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-12-12
Source: https://osv.dev/vulnerability/CVE-2018-20098
Type: osv

## Details
There is a heap-based buffer over-read in Exiv2::Jp2Image::encodeJp2Header of jp2image.cpp in Exiv2 0.27-RC3. A crafted input will lead to a remote denial of service attack.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZXCEKTYF7HLM6VH2WCWO2HXTJH37MBLA/
- https://access.redhat.com/errata/RHSA-2019:2101
- https://github.com/TeamSeri0us/pocs/tree/master/exiv2/20181206
- https://github.com/Exiv2/exiv2/issues/590
