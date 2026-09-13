# [C] org.xwiki.platform:xwiki-platform-logging-ui Injection vulnerability

## Summary
Severity: Critical
Advisory: CVE-2023-29213
Aliases: GHSA-4655-wh7v-3vmg
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2023-04-17
Source: https://osv.dev/vulnerability/CVE-2023-29213
Type: osv

## Details
XWiki Platform is a generic wiki platform offering runtime services for applications built on top of it. In affected versions of `org.xwiki.platform:xwiki-platform-logging-ui` it is possible to trick a user with programming rights into visiting a constructed url where e.g., by embedding an image with this URL in a document that is viewed by a user with programming rights which will evaluate an expression in the constructed url and execute it. This issue has been addressed in versions 13.10.11, 14.4.7, and 14.10. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://jira.xwiki.org/browse/XWIKI-20291
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29213.json
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-4655-wh7v-3vmg
- https://nvd.nist.gov/vuln/detail/CVE-2023-29213
- https://github.com/xwiki/xwiki-platform/commit/49fdfd633ddfa346c522d2fe71754dc72c9496ca
