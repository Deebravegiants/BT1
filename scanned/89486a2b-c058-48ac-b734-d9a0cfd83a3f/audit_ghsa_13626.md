# [H] XWiki Rendering's footnote macro vulnerable to privilege escalation via the footnote macro

## Summary
Severity: High
Advisory: GHSA-35j5-m29r-xfq5
CVE: CVE-2023-37912
CWE: CWE-270
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-25
Source: https://github.com/advisories/GHSA-35j5-m29r-xfq5
Type: github-advisory

## Affected
- Maven: `org.xwiki.rendering:xwiki-rendering-macro-footnotes` — affected >=0 <14.10.6
- Maven: `org.xwiki.rendering:xwiki-rendering-macro-footnotes` — affected >=15.0-rc-1 <15.1-rc-1
- Maven: `org.xwiki.platform:xwiki-core-rendering-macro-footnotes` — affected >=0 <14.10.6

## Details
### Impact

The footnote macro executed its content in a potentially different context than the one in which it was defined. In particular in combination with the include macro, this allows privilege escalation from a simple user account in XWiki to programming rights and thus remote code execution, impacting the confidentiality, integrity and availability of the whole XWiki installation.

To reproduce, perform the following steps:

1. Edit your user profile with the object editor and add an object of type DocumentSheetBinding with value XWiki.ClassSheet
2. Edit your user profile with the wiki editor and add the syntax `{{footnote}}{{groovy}}println("Hello " + "from groovy!"){{/groovy}}{{/footnote}}`

When the text "Hello from groovy!" is displayed at the bottom of the document, the installation is vulnerable. Instead, an error should be displayed.

### Patches
This vulnerability has been patched in XWiki 14.10.6 and 15.1-rc-1.

### Workarounds
There is no workaround apart from upgrading to a fixed version of the footnote macro.

### References
* https://jira.xwiki.org/browse/XRENDERING-688
* https://github.com/xwiki/xwiki-rendering/commit/5f558b8fac8b716d19999225f38cb8ed0814116e

## References
- https://github.com/xwiki/xwiki-rendering/security/advisories/GHSA-35j5-m29r-xfq5
- https://nvd.nist.gov/vuln/detail/CVE-2023-37912
- https://github.com/xwiki/xwiki-rendering/commit/5f558b8fac8b716d19999225f38cb8ed0814116e
- https://github.com/xwiki/xwiki-rendering
- https://jira.xwiki.org/browse/XRENDERING-688
