# [M] eml_parser has a URL extraction bypass via HTML entities in URLs

## Summary
Severity: Medium
Advisory: GHSA-fxgq-9m89-cxj9
CVE: CVE-2026-55618
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-fxgq-9m89-cxj9
Type: github-advisory

## Affected
- PyPI: `eml_parser` — affected >=0 <3.0.2

## Details
## Summary

`eml_parser` performs certain validations on potential URL strings to discard bogus values. In versions prior to `3.0.2`, this validation was performed before unescaping any HTML entities that might occur in the string. This caused the library to wrongfully reject valid URLs that use HTML entities for the `:`, `/`, or `.` characters. These URLs would then not be included in the list of extracted URLs. Similarly, the host parts of such URLs would not be extracted.

For example, neither the URL `https&#58;&#47;&#47;phishing&#46;example&#46;com` nor its host (`phishing.example.com`) would appear in the parsing result.

## Impact

`eml_parser` is used in email security gateways and SOC pipelines to extract URLs as IOCs. Those URLs are then checked against threat-intel feeds, URL reputation services, and sandboxes. A URL that is not extracted is never checked.

## Patches

Since version 3.0.2 the library unescapes all HTML entities in every URL before deciding to accept or reject it. A test was added to prevent regressions.

## References
- https://github.com/GOVCERT-LU/eml_parser/security/advisories/GHSA-fxgq-9m89-cxj9
- https://github.com/GOVCERT-LU/eml_parser/pull/90
- https://github.com/GOVCERT-LU/eml_parser/commit/746a69f86443eb0b6a47f77db3cfe727c21f92b3
- https://github.com/GOVCERT-LU/eml_parser
- https://github.com/GOVCERT-LU/eml_parser/releases/tag/v3.0.2
