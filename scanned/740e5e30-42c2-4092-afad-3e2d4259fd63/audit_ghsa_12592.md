# [C] XWiki Platform vulnerable to reflected cross-site scripting via xredirect parameter in DeleteApplication page

## Summary
Severity: Critical
Advisory: GHSA-4xm7-5q79-3fch
CVE: CVE-2023-35161
CWE: CWE-79, CWE-87
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-4xm7-5q79-3fch
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=6.2-milestone-1 <14.10.5
- Maven: `org.xwiki.platform:xwiki-platform-appwithinminutes-ui` — affected >=15.0-rc-1 <15.1-rc-1

## Details
### Impact
Users are able to forge an URL with a payload allowing to inject Javascript in the page (XSS).
It's possible to exploit the DeleteApplication page to perform a XSS, e.g. by using URL such as:

> xwiki/bin/view/AppWithinMinutes/DeleteApplication?appName=Menu&resolve=true&xredirect=javascript:alert(document.domain)

This vulnerability exists since XWiki 6.2-milestone-1.

### Patches

The vulnerability has been patched in XWiki 14.10.5 and 15.1-rc-1.

### Workarounds

It's possible to workaround the vulnerability by editing the page AppWithinMinutes.DeleteApplication to perform checks on it, but note that the appropriate fix involves new APIs that have been recently introduced in XWiki. See the referenced jira tickets.

### References

  * Jira ticket about the vulnerability: https://jira.xwiki.org/browse/XWIKI-20614
  * Introduction of the macro used for fixing all those vulnerabilities: https://jira.xwiki.org/browse/XWIKI-20583
  * Commit containing the actual fix in the page: https://github.com/xwiki/xwiki-platform/commit/8f5a889b7cd140770e54f5b4195d88058790e305

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-4xm7-5q79-3fch
- https://nvd.nist.gov/vuln/detail/CVE-2023-35161
- https://github.com/xwiki/xwiki-platform/commit/8f5a889b7cd140770e54f5b4195d88058790e305
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20583
- https://jira.xwiki.org/browse/XWIKI-20614
