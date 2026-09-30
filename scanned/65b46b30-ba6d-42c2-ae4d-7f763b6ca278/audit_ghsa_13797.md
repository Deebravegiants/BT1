# [C] XWiki Platform privilege escalation from script right to programming right through title displayer

## Summary
Severity: Critical
Advisory: GHSA-rmxw-c48h-2vf5
CVE: CVE-2023-46244
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-11-07
Source: https://github.com/advisories/GHSA-rmxw-c48h-2vf5
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-display-api` — affected >=3.2-milestone-3 <14.10.7
- Maven: `org.xwiki.platform:xwiki-platform-display-api` — affected >=15.0 <15.2-rc-1

## Details
### Impact

In XWiki Platform, it's possible for a user to write a script in which any velocity content is executed with the right of any other document content author.

To reproduce:

As a user with script but not programming right, create a document with the following content:

```
{{velocity}}
#set($main = $xwiki.getDocument('AppWithinMinutes.DynamicMessageTool'))
$main.setTitle('$doc.getDocument().getContentAuthor()')
$main.getPlainTitle()
{{/velocity}}
```

Since this API require programming right and the user does not have it, the expected result is `$doc.document.authors.contentAuthor` (not executed script), unfortunately with the security vulnerability we get `XWiki.superadmin` which shows that the title was executed with the right of the unmodified document.

### Patches

This has been patched in XWiki 14.10.7 and 15.2-RC-1.

### Workarounds

There are no known workarounds for it.

### References

* https://jira.xwiki.org/browse/XWIKI-20624
* https://github.com/xwiki/xwiki-platform/commit/11a9170dfe63e59f4066db67f84dbfce4ed619c6
* https://jira.xwiki.org/browse/XWIKI-20625
* https://github.com/xwiki/xwiki-platform/commit/41d7dca2d30084966ca6a7ee537f39ee8354a7e3

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki.org](https://jira.xwiki.org/)
* Email us at [Security Mailing List](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-rmxw-c48h-2vf5
- https://nvd.nist.gov/vuln/detail/CVE-2023-46244
- https://github.com/xwiki/xwiki-platform/commit/11a9170dfe63e59f4066db67f84dbfce4ed619c6
- https://github.com/xwiki/xwiki-platform/commit/41d7dca2d30084966ca6a7ee537f39ee8354a7e3
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-20624
- https://jira.xwiki.org/browse/XWIKI-20625
