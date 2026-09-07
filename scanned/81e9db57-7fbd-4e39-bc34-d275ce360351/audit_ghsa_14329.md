# [H] Improper Neutralization of Script-Related HTML Tags (XSS) in the LiveTable Macro

## Summary
Severity: High
Advisory: GHSA-6vgh-9r3c-2cxp
CVE: CVE-2023-29207
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-6vgh-9r3c-2cxp
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin-resources` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-flamingo` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-web-standard` — affected >=1.9-milestone-2 <13.10.10
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin-resources` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-flamingo` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-web-standard` — affected >=14.0-rc-1 <14.4.6
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin-resources` — affected >=14.5 <14.9
- Maven: `org.xwiki.platform:xwiki-platform-flamingo-skin` — affected >=14.5 <14.9
- Maven: `org.xwiki.platform:xwiki-platform-flamingo` — affected >=14.5 <14.9
- Maven: `org.xwiki.platform:xwiki-platform-web-templates` — affected >=14.5 <14.9
- Maven: `org.xwiki.platform:xwiki-platform-web` — affected >=14.5 <14.9
- Maven: `org.xwiki.platform:xwiki-web-standard` — affected >=14.5 <14.9

## Details
### Impact
The [Livetable Macro](https://extensions.xwiki.org/xwiki/bin/view/Extension/Livetable%20Macro) wasn't properly sanitizing column names, thus allowing the insertion of raw HTML code including JavaScript. This vulnerability was also exploitable via the [Documents Macro](https://extensions.xwiki.org/xwiki/bin/view/Extension/Documents%20Macro) that is included since XWiki 3.5M1 and doesn't require script rights, this can be demonstrated with the syntax `{{documents id="example" count="5" actions="false" columns="doc.title, before<script>alert(1)</script>after"/}}`. Therefore, this can also be exploited by users without script right and in comments. With the interaction of a user with more rights, this could be used to execute arbitrary actions in the wiki, including privilege escalation, remote code execution, information disclosure, modifying or deleting content.

### Patches
This has been patched in XWiki 14.9, 14.4.6, and 13.10.10.

### Workarounds
It is possible to apply the [patch](https://github.com/xwiki/xwiki-platform/commit/65ca06c51e7a1d5a579344c7272b2cc9a9a21126) to existing installations without upgrading. Only the files `skins/flamingo/macros.vm` and `templates/macros.vm` in the web application directory need to be replaced by a patched version.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-6vgh-9r3c-2cxp
- https://nvd.nist.gov/vuln/detail/CVE-2023-29207
- https://github.com/xwiki/xwiki-platform/commit/65ca06c51e7a1d5a579344c7272b2cc9a9a21126
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-15205
