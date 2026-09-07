# [H] XWiki Platform vulnerable to cross-site scripting in target parameter via share page by email

## Summary
Severity: High
Advisory: GHSA-fwwj-wg89-7h4c
CVE: CVE-2023-35155
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-06-20
Source: https://github.com/advisories/GHSA-fwwj-wg89-7h4c
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-sharepage-api` — affected >=2.6-rc-2 <14.4.8
- Maven: `org.xwiki.platform:xwiki-platform-sharepage-api` — affected >=14.5 <14.10.4

## Details
### Impact
Users are able to forge an URL with a payload allowing to inject Javascript in the page (XSS).
For instance, the following URL execute an `alter` on the browser: `<xwiki-host>/xwiki/bin/view/Main/?viewer=share&send=1&target=&target=%3Cimg+src+onerror%3Dalert%28document.domain%29%3E+%3Cimg+src+onerror%3Dalert%28document.domain%29%3E+%3Crenniepak%40intigriti.me%3E&includeDocument=inline&message=I+wanted+to+share+this+page+with+you.`, where `<xwiki-host>` is the URL of your XWiki installation.
See https://jira.xwiki.org/browse/XWIKI-20370 for me details.

### Patches

The vulnerability has been patched in XWiki 15.0-rc-1, 14.10.4, and 14.4.8.

### Workarounds
The fix is only impacting Velocity templates and page contents, so applying this [patch](https://github.com/xwiki/xwiki-platform/commit/ca88ebdefb2c9fa41490959cce9f9e62404799e7) is enough to fix the issue.

### References
https://jira.xwiki.org/browse/XWIKI-20370

### For more information

If you have any questions or comments about this advisory:

*    Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
*    Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-fwwj-wg89-7h4c
- https://nvd.nist.gov/vuln/detail/CVE-2023-35155
- https://github.com/xwiki/xwiki-platform/commit/ca88ebdefb2c9fa41490959cce9f9e62404799e7
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20370
