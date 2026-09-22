# [C] CVE-2020-25614

## Summary
Severity: Critical
Advisory: CVE-2020-25614
Aliases: GHSA-93m7-c69f-5cfj, GO-2020-0048
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-25614
Type: osv

## Details
xmlquery before 1.3.1 lacks a check for whether a LoadURL response is in the XML format, which allows attackers to cause a denial of service (SIGSEGV) at xmlquery.(*Node).InnerText or possibly have unspecified other impact.

## References
- https://github.com/antchfx/xmlquery/compare/v1.3.0...v1.3.1
- https://github.com/antchfx/xmlquery/issues/39
