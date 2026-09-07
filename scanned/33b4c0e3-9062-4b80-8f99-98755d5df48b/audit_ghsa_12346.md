# [H] Apache Tiles: Unvalidated input may lead to path traversal and XXE

## Summary
Severity: High
Advisory: GHSA-qw4h-3xjj-84cc
CVE: CVE-2023-49735
CWE: CWE-22, CWE-776
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-qw4h-3xjj-84cc
Type: github-advisory

## Affected
- Maven: `org.apache.tiles:tiles-core` — affected >=2.0.0
- Maven: `org.apache.struts:struts-tiles` — affected >=1.3.0
- Maven: `struts:struts` — affected >=1.1

## Details
The value set as the DefaultLocaleResolver.LOCALE_KEY attribute on the session was not validated while resolving XML definition files, leading to possible path traversal and eventually SSRF/XXE when passing user-controlled data to this key. Passing user-controlled data to this key may be relatively common, as it was also used like that to set the language in the 'tiles-test' application shipped with Tiles.

This issue affects Apache Tiles from version 2 onwards.

NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-49735
- https://github.com/apache/tiles
- https://lists.apache.org/thread/8ktm4vxr6vvc1qsxh6ft8jzmom1zl65p
