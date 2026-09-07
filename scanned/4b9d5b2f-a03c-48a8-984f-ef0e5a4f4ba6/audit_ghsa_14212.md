# [C] org.xwiki.platform:xwiki-platform-skin-skinx vulnerable to basic Cross-site Scripting by exploiting JSX or SSX plugins

## Summary
Severity: Critical
Advisory: GHSA-cmvg-w72j-7phx
CVE: CVE-2023-29206
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-cmvg-w72j-7phx
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-skin-skinx` — affected >=3.0-milestone-1 <14.9-rc-1

## Details
### Impact

There was no check in the author of a JavaScript xobject or StyleSheet xobject added in a XWiki document, so until now it was possible for a user having only Edit Right to create such object and to craft a script allowing to perform some operations when executing by a user with appropriate rights. 

### Patches

This has been patched in XWiki 14.9-rc-1 by only executing the script if the author of it has Script right. 

### Workarounds

The only known workaround consists in applying [the following patch](https://github.com/xwiki/xwiki-platform/commit/fe65bc35d5672dd2505b7ac4ec42aec57d500fbb) and rebuilding and redeploying `xwiki-platform-skin-skinx`.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](http://jira.xwiki.org)
* Email us at [Security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-cmvg-w72j-7phx
- https://nvd.nist.gov/vuln/detail/CVE-2023-29206
- https://github.com/xwiki/xwiki-platform/commit/fe65bc35d5672dd2505b7ac4ec42aec57d500fbb
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-19514
- https://jira.xwiki.org/browse/XWIKI-19583
- https://jira.xwiki.org/browse/XWIKI-9119
