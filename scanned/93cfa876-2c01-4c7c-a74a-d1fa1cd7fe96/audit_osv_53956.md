# [H] CVE-2023-34194

## Summary
Severity: High
Advisory: CVE-2023-34194
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-13
Source: https://osv.dev/vulnerability/CVE-2023-34194
Type: osv

## Details
StringEqual in TiXmlDeclaration::Parse in tinyxmlparser.cpp in TinyXML through 2.6.2 has a reachable assertion (and application exit) via a crafted XML document with a '\0' located after whitespace.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00024.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4QCR5PIOBGDIDS6SYRESTMDJSEDFSCOE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HOMBSHRIW5Q34SQSXYURYAOYDZD2NQF6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4QCR5PIOBGDIDS6SYRESTMDJSEDFSCOE/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HOMBSHRIW5Q34SQSXYURYAOYDZD2NQF6/
- https://www.forescout.com/resources/sierra21-vulnerabilities
- https://sourceforge.net/p/tinyxml/git/ci/master/tree/tinyxmlparser.cpp
