# [H] CVE-2016-7051

## Summary
Severity: High
Advisory: CVE-2016-7051
Aliases: GHSA-7c2r-3jqf-c9rw
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/CVE-2016-7051
Type: osv

## Details
XmlMapper in the Jackson XML dataformat component (aka jackson-dataformat-xml) before 2.7.8 and 2.8.x before 2.8.4 allows remote attackers to conduct server-side request forgery (SSRF) attacks via vectors related to a DTD.

## References
- http://www.securityfocus.com/bid/97688
- https://bugzilla.redhat.com/show_bug.cgi?id=1378673
- https://github.com/FasterXML/jackson-dataformat-xml/issues/211
