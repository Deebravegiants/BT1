# [C] Improper Neutralization of Script in Attributes in XWiki (X)HTML renderers

## Summary
Severity: Critical
Advisory: GHSA-6gf5-c898-7rxp
CVE: CVE-2023-32070
CWE: CWE-79, CWE-83
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-6gf5-c898-7rxp
Type: github-advisory

## Affected
- Maven: `org.xwiki.rendering:xwiki-rendering-syntax-xhtml` — affected >=0 <14.6-rc-1
- Maven: `org.xwiki.platform:xwiki-core-rendering-api` — affected >=0
- Maven: `org.xwiki.rendering:xwiki-rendering-syntax-html` — affected >=0 <14.6-rc-1
- Maven: `org.xwiki.rendering:xwiki-rendering-syntax-html5` — affected >=0 <14.6-rc-1
- Maven: `org.xwiki.rendering:xwiki-rendering-syntax-annotatedxhtml` — affected >=0 <14.6-rc-1
- Maven: `org.xwiki.rendering:xwiki-rendering-syntax-annotatedhtml5` — affected >=0 <14.6-rc-1
- Maven: `org.xwiki.platform:xwiki-platform-annotation-core` — affected >=0 <14.6-rc-1

## Details
### Impact

HTML rendering didn't check for dangerous attributes/attribute values. This allowed cross-site scripting (XSS) attacks via attributes and link URLs, e.g., supported in XWiki syntax.

### Patches
This has been patched in XWiki 14.6 RC1.

### Workarounds
There are no known workarounds apart from upgrading to a fixed version.

### References
* https://github.com/xwiki/xwiki-rendering/commit/c40e2f5f9482ec6c3e71dbf1fff5ba8a5e44cdc1
* https://jira.xwiki.org/browse/XRENDERING-663

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-rendering/security/advisories/GHSA-6gf5-c898-7rxp
- https://nvd.nist.gov/vuln/detail/CVE-2023-32070
- https://github.com/xwiki/xwiki-rendering/commit/c40e2f5f9482ec6c3e71dbf1fff5ba8a5e44cdc1
- https://github.com/xwiki/xwiki-rendering
- https://jira.xwiki.org/browse/XRENDERING-663
