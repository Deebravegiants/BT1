# [C] XWiki Platform vulnerable to reflected cross-site scripting via back and xcontinue parameters in resubmit template

## Summary
Severity: Critical
Advisory: GHSA-r8xc-xxh3-q5x3
CVE: CVE-2023-35160
CWE: CWE-79, CWE-87
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-22
Source: https://github.com/advisories/GHSA-r8xc-xxh3-q5x3
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=2.5-milestone-2 <14.10.5
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=15.0-rc-1 <15.1-rc-1

## Details
### Impact
Users are able to forge an URL with a payload allowing to inject Javascript in the page (XSS).
It's possible to exploit the resubmit template to perform a XSS, e.g. by using URL such as:

 > xwiki/bin/view/XWiki/Main?xpage=resubmit&resubmit=javascript:alert(document.domain)&xback=javascript:alert(document.domain)

This vulnerability exists since XWiki 2.5-milestone-2.

### Patches

The vulnerability has been patched in XWiki 14.10.5 and 15.1-rc-1.

### Workarounds

It's possible to workaround the vulnerability by editing the template resubmit.vm to perform checks on it, but note that the appropriate fix involves new APIs that have been recently introduced in XWiki. See the referenced jira tickets.

### References

  * Jira ticket about the vulnerability: https://jira.xwiki.org/browse/XWIKI-20343
  * Introduction of the macro used for fixing all those vulnerabilities: https://jira.xwiki.org/browse/XWIKI-20583
  * Commit containing the actual fix in the page: https://github.com/xwiki/xwiki-platform/commit/dbc92dcdace33823ffd1e1591617006cb5fc6a7f

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-r8xc-xxh3-q5x3
- https://nvd.nist.gov/vuln/detail/CVE-2023-35160
- https://github.com/xwiki/xwiki-platform/commit/dbc92dcdace33823ffd1e1591617006cb5fc6a7f
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20343
- https://jira.xwiki.org/browse/XWIKI-20583
