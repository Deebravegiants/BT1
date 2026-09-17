# [H] CVE-2021-42260

## Summary
Severity: High
Advisory: CVE-2021-42260
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-10-11
Source: https://osv.dev/vulnerability/CVE-2021-42260
Type: osv

## Details
TinyXML through 2.6.2 has an infinite loop in TiXmlParsingData::Stamp in tinyxmlparser.cpp via the TIXML_UTF_LEAD_0 case. It can be triggered by a crafted XML message and leads to a denial of service.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4QCR5PIOBGDIDS6SYRESTMDJSEDFSCOE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HOMBSHRIW5Q34SQSXYURYAOYDZD2NQF6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4QCR5PIOBGDIDS6SYRESTMDJSEDFSCOE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HOMBSHRIW5Q34SQSXYURYAOYDZD2NQF6/
- https://lists.debian.org/debian-lts-announce/2022/09/msg00041.html
- https://lists.debian.org/debian-lts-announce/2022/04/msg00019.html
- https://sourceforge.net/p/tinyxml/bugs/141/
