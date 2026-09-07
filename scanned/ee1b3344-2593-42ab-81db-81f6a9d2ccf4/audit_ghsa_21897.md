# [M] Partial authorization bypass on document save in xwiki-platform

## Summary
Severity: Medium
Advisory: GHSA-f4cj-3q3h-884r
CVE: CVE-2022-23615
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-f4cj-3q3h-884r
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=1.0 <13.0

## Details
XWiki Platform is a generic wiki platform offering runtime services for applications built on top of it. Any user with SCRIPT right (EDIT right before XWiki 7.4) can save a document with the right of the current user which allow accessing API requiring programming right if the current user has programming right. It has been patched in XWiki 13.0. The only workaround is to give SCRIPT right only to trusted users.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-f4cj-3q3h-884r
- https://nvd.nist.gov/vuln/detail/CVE-2022-23615
- https://github.com/xwiki/xwiki-platform/commit/7ab0fe7b96809c7a3881454147598d46a1c9bbbe
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-5024
