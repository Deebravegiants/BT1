# [C] org.xwiki.platform:xwiki-platform-rendering-xwiki vulnerable to stored cross-site scripting via HTML and raw macro

## Summary
Severity: Critical
Advisory: GHSA-vxf7-mx22-jr24
CVE: CVE-2023-29205
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-12
Source: https://github.com/advisories/GHSA-vxf7-mx22-jr24
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-rendering-xwiki` — affected >=0 <14.8-rc-1

## Details
### Impact

The HTML macro does not systematically perform a proper neutralization of script-related html tags. As a result, any user able to use the html macro in XWiki, is able to introduce an XSS attack. This can be particularly dangerous since in a standard wiki, any user is able to use the html macro directly in their own user profile page. 

### Patches

The problem has been patched in XWiki 14.8RC1. The patch involve that the HTML macro are systematically cleaned up whenever the user does not have script right. 

### Workarounds

There's no workaround for this issue.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [Jira](https://jira.xwiki.org)
* Email us at [security ML](mailto:security@xwiki.org)

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-vxf7-mx22-jr24
- https://nvd.nist.gov/vuln/detail/CVE-2023-29205
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-18568
