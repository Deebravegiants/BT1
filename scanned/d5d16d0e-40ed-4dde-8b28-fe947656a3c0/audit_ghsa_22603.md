# [H] Cross-site Scripting in wiki manager join wiki page

## Summary
Severity: High
Advisory: GHSA-ph5x-h23x-7q5q
CVE: CVE-2022-29252
CWE: CWE-116, CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-25
Source: https://github.com/advisories/GHSA-ph5x-h23x-7q5q
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=0 <12.10.11
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=13.0.0 <13.4.7
- Maven: `org.xwiki.platform:xwiki-platform-wiki-ui-mainwiki` — affected >=13.5.0 <13.10.3

## Details
### Impact
We found a possible XSS vector in the `WikiManager.JoinWiki ` wiki page related to the "requestJoin" field.

### Patches
The issue is patched in versions 12.10.11, 14.0-rc-1, 13.4.7, 13.10.3.

### Workarounds
The easiest workaround is to edit the wiki page `WikiManager.JoinWiki` (with wiki editor) and change the line

```
<input type='hidden' name='requestJoin' value="$!request.requestJoin"/>
```

into

```
<input type='hidden' name='requestJoin' value="$escapetool.xml($!request.requestJoin)">
```

### References
  * https://jira.xwiki.org/browse/XWIKI-19292
  * https://github.com/xwiki/xwiki-platform/commit/27f839133d41877e538d35fa88274b50a1c00b9b

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira XWiki](https://jira.xwiki.org)
* Email us at [security mailing list](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-ph5x-h23x-7q5q
- https://nvd.nist.gov/vuln/detail/CVE-2022-29252
- https://github.com/xwiki/xwiki-platform/commit/27f839133d41877e538d35fa88274b50a1c00b9b
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19292
