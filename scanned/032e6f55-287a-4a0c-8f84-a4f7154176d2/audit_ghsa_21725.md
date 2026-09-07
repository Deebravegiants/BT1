# [M] Path traversal in xwiki-platform-skin-skinx

## Summary
Severity: Medium
Advisory: GHSA-7ph6-5cmq-xgjq
CVE: CVE-2022-23620
CWE: CWE-116, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:C/C:L/I:L/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-7ph6-5cmq-xgjq
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=6.2-rc-1 <13.6

## Details
XWiki Platform is a generic wiki platform offering runtime services for applications built on top of it. AbstractSxExportURLFactoryActionHandler#processSx does not escape anything from SSX document reference when serializing it on filesystem, so it's easy to mess up the HTML export process with reference elements containing filesystem syntax like "../", "./". or "/" in general (the last two not causing any security threat, but can cause conflicts with others serialized files). Patch can be found in 13.6-rc-1. Giving script or subwiki admin right only to trusted people and disabling HTML/PDF export can be done as workaround.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-7ph6-5cmq-xgjq
- https://nvd.nist.gov/vuln/detail/CVE-2022-23620
- https://github.com/xwiki/xwiki-platform/commit/ab778254fb8f71c774e1c1239368c44fe3b6bba5
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18819
