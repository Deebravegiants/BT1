# [C] XWiki Rendering is vulnerable to RCE attacks when processing nested macros

## Summary
Severity: Critical
Advisory: GHSA-32mf-57h2-64x9
CVE: CVE-2025-53836
CWE: CWE-863, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-07-14
Source: https://github.com/advisories/GHSA-32mf-57h2-64x9
Type: github-advisory

## Affected
- Maven: `org.xwiki.rendering:xwiki-rendering-transformation-macro` — affected >=4.2-milestone-1 <13.10.11
- Maven: `org.xwiki.rendering:xwiki-rendering-transformation-macro` — affected >=14.0 <14.4.7
- Maven: `org.xwiki.rendering:xwiki-rendering-transformation-macro` — affected >=14.5 <14.10

## Details
### Impact

The default macro content parser didn't preserve the restricted attribute of the transformation context when executing nested macros. This allows executing macros that are normally forbidden in restricted mode, in particular script macros. The [cache](https://extensions.xwiki.org/xwiki/bin/view/Extension/Cache%20Macro) and [chart](https://extensions.xwiki.org/xwiki/bin/view/Extension/Chart%20Macro) macros that are bundled in XWiki use the vulnerable feature. The following XWiki syntax, when used inside a comment in XWiki, demonstrates the privilege escalation from comment right to programming right and thus remote code execution (RCE) that is possible due to this:

```
{{cache}}{{groovy}}println("Hello from Groovy!"){{/groovy}}{{/cache}}
```

This vulnerability exists since the restricted attribute has been added to the transformation context in version 4.2.

### Patches
This has been patched in XWiki 13.10.11, 14.4.7 and 14.10.

### Workarounds
To avoid the exploitation of this bug, comments can be disabled for untrusted users until an upgrade to a patched version has been performed. Note that users with edit rights will still be able to add comments via the object editor even if comments have been disabled.

### Resources
* https://github.com/xwiki/xwiki-rendering/commit/c73fa3ccd4ac59057e48e5d4325f659e78e8f86d
* https://jira.xwiki.org/browse/XRENDERING-689
* https://jira.xwiki.org/browse/XWIKI-20375

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

### Attribution

This vulnerability has been reported on Intigriti by René de Sain @renniepak.

## References
- https://github.com/xwiki/xwiki-rendering/security/advisories/GHSA-32mf-57h2-64x9
- https://nvd.nist.gov/vuln/detail/CVE-2025-53836
- https://github.com/xwiki/xwiki-rendering/commit/c73fa3ccd4ac59057e48e5d4325f659e78e8f86d
- https://github.com/xwiki/xwiki-rendering
- https://jira.xwiki.org/browse/XRENDERING-689
- https://jira.xwiki.org/browse/XWIKI-20375
